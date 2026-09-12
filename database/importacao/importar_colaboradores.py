import pandas as pd
from pathlib import Path

from database.database import SessionLocal
from database.depara import secao_tratada, tipos_ccusto_dos_rateios
from database.models import Colaborador, Rateio


ARQUIVO_EXCEL = Path(__file__).resolve().parent / "cadastro.xlsx"

COLUNAS_OBRIGATORIAS = ("CHAPA", "NOME", "FUNÇÃO", "ADMISSÃO", "SEÇÃO", "SITUAÇÃO")


def normalizar_linha_colaborador(linha):
    """Le e valida uma linha do Excel de cadastro. Devolve (dados, erro).

    Reaproveitada tanto pelo script standalone quanto pelos endpoints web
    (previa/aplicar), para as duas vias terem exatamente a mesma regra.
    """
    chapa_bruta = linha.get("CHAPA")
    if chapa_bruta is None or (isinstance(chapa_bruta, float) and pd.isna(chapa_bruta)):
        return None, "CHAPA não informada."

    chapa = str(chapa_bruta).strip()
    if chapa.endswith(".0"):
        chapa = chapa[:-2]
    if not chapa:
        return None, "CHAPA não informada."

    admissao = pd.to_datetime(linha.get("ADMISSÃO"), dayfirst=True, errors="coerce")
    admissao = None if pd.isna(admissao) else admissao.date()

    rateio_funcionario = linha.get("RATEIO_FUNCIONARIO")
    rateio_funcionario = (
        None if pd.isna(rateio_funcionario) else str(rateio_funcionario).strip()
    )
    if rateio_funcionario == "":
        rateio_funcionario = None

    grpccusto = linha.get("GRPCCUSTO")
    grpccusto = None if pd.isna(grpccusto) else str(grpccusto).strip()

    def texto(valor):
        if valor is None or (isinstance(valor, float) and pd.isna(valor)):
            return None
        return str(valor).strip()

    return {
        "chapa": chapa,
        "NOME": texto(linha.get("NOME")),
        "FUNÇÃO": texto(linha.get("FUNÇÃO")),
        "ADMISSÃO": admissao,
        "SEÇÃO": texto(linha.get("SEÇÃO")),
        "SITUAÇÃO": texto(linha.get("SITUAÇÃO")),
        "rateio_funcionario": rateio_funcionario,
        "grpccusto": grpccusto,
    }, None


RÓTULOS_CAMPOS = {
    "NOME": "Nome",
    "FUNÇÃO": "Função",
    "ADMISSÃO": "Admissão",
    "SEÇÃO": "Seção",
    "SITUAÇÃO": "Situação",
}


def _texto_exibicao(valor):
    """Formata um valor de campo (string, date ou None) pro 'de-para' que a
    tela de Usuários mostra — sempre texto, nunca objeto date/None cru."""
    if valor is None:
        return "—"
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def processar_planilha_colaboradores(arquivo, session, aplicar):
    """Le a planilha inteira e faz o upsert de todos os colaboradores/rateios
    na sessao dada, em lote — nao linha a linha.

    A planilha real (cadastro.xlsx) tem uma linha por CHAPA+rateio, entao um
    cadastro de ~1200 colaboradores facilmente passa de 1200 linhas. A versao
    anterior fazia 1 SELECT + 1 flush por linha (contra o Postgres remoto da
    Neon, sem banco local de desenvolvimento — ver banco-producao-neon na
    memoria do projeto), o que estourava o timeout do navegador antes de
    terminar. Aqui a busca dos colaboradores/rateios existentes e feita uma
    unica vez (2 SELECTs com IN, nao N), e o flush por linha foi removido —
    ele so existia para o Rateio enxergar o id do Colaborador recem-criado,
    mas Rateio.CHAPA referencia Colaborador.CHAPA (a chave de negocio, nao o
    id serial), entao o flush nunca foi necessario.

    aplicar=False roda a mesma lógica de upsert mas o chamador é quem decide
    se comita ou dá rollback (usado para gerar uma prévia sem gravar nada).
    Devolve um resumo com contagens (por CHAPA unica, nao por linha — uma
    chapa com 3 linhas de rateio conta 1 vez em criados/atualizados) e erros
    por linha.
    """
    try:
        df = pd.read_excel(arquivo)
    except Exception as erro:
        raise ValueError(f"Não foi possível ler a planilha: {erro}")

    colunas = {str(c).strip() for c in df.columns}
    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in colunas]
    if faltando:
        raise ValueError(f"A planilha precisa das colunas {', '.join(faltando)}.")

    resumo = {
        "criados": 0,
        "atualizados": 0,
        "rateios_novos": 0,
        "erros": [],
        # "de-para" pra tela de Usuários: 1 entrada por CHAPA (nao por linha
        # de rateio), pra clicar no chip "novos"/"atualizados" e ver o que
        # mudou de fato
        "detalhes_criados": [],
        "detalhes_atualizados": [],
        "detalhes_rateios": [],
    }

    def _celula(linha, coluna):
        """Valor cru de uma célula, já como texto — usado só pra IDENTIFICAR a
        linha com erro na tela (a linha nem passou pela normalização)."""
        valor = linha.get(coluna)
        if valor is None or (isinstance(valor, float) and pd.isna(valor)):
            return ""
        texto = str(valor).strip()
        return texto[:-2] if texto.endswith(".0") else texto

    linhas_validas = []
    for indice, linha in df.iterrows():
        numero = int(indice) + 2
        dados, erro = normalizar_linha_colaborador(linha)
        if erro:
            resumo["erros"].append({
                "linha": numero,
                "erro": erro,
                "chapa": _celula(linha, "CHAPA"),
                "nome": _celula(linha, "NOME"),
                "secao": _celula(linha, "SEÇÃO"),
            })
            continue
        linhas_validas.append(dados)

    if not linhas_validas:
        return resumo

    chapas = {dados["chapa"] for dados in linhas_validas}

    colaboradores_existentes = {
        c.CHAPA: c
        for c in session.query(Colaborador).filter(Colaborador.CHAPA.in_(chapas)).all()
    }

    rateios_existentes = {
        (r.CHAPA, r.RATEIO_FUNCIONARIO, r.GRPCCUSTO)
        for r in session.query(Rateio).filter(Rateio.CHAPA.in_(chapas)).all()
    }

    # CHAPA -> códigos de rateio (existentes + os que essa planilha for
    # adicionar), pra calcular TIPO_CCUSTO com TODOS os rateios do
    # colaborador no final — não só o primeiro. Semeado com os rateios que
    # já existiam antes desta importação (podem ter vindo de outra
    # planilha, outro dia).
    codigos_rateio_por_chapa = {}
    for chapa_r, codigo_r, _grpccusto_r in rateios_existentes:
        if codigo_r:
            codigos_rateio_por_chapa.setdefault(chapa_r, []).append(codigo_r)

    chapas_ja_contadas = set()
    rateios_ja_adicionados = set()

    for dados in linhas_validas:
        chapa = dados["chapa"]
        campos = {
            campo: dados[campo]
            for campo in ("NOME", "FUNÇÃO", "ADMISSÃO", "SEÇÃO", "SITUAÇÃO")
        }

        primeira_vez = chapa not in chapas_ja_contadas
        colaborador = colaboradores_existentes.get(chapa)
        if colaborador:
            if primeira_vez:
                mudancas = [
                    {
                        "campo": RÓTULOS_CAMPOS[campo],
                        "de": _texto_exibicao(getattr(colaborador, campo)),
                        "para": _texto_exibicao(valor),
                    }
                    for campo, valor in campos.items()
                    if getattr(colaborador, campo) != valor
                ]
                resumo["detalhes_atualizados"].append({
                    "chapa": chapa,
                    "nome": campos["NOME"] or colaborador.NOME or "",
                    "mudancas": mudancas,
                })

            for campo, valor in campos.items():
                setattr(colaborador, campo, valor)
            if primeira_vez:
                resumo["atualizados"] += 1
        else:
            colaborador = Colaborador(CHAPA=chapa, **campos)
            session.add(colaborador)
            colaboradores_existentes[chapa] = colaborador
            if primeira_vez:
                resumo["criados"] += 1
                resumo["detalhes_criados"].append({
                    "chapa": chapa,
                    "nome": campos["NOME"] or "",
                    "funcao": campos["FUNÇÃO"] or "",
                    "secao": campos["SEÇÃO"] or "",
                    "situacao": campos["SITUAÇÃO"] or "",
                    "admissao": _texto_exibicao(campos["ADMISSÃO"]),
                })

        chapas_ja_contadas.add(chapa)

        if dados["rateio_funcionario"]:
            chave = (chapa, dados["rateio_funcionario"], dados["grpccusto"])
            if chave not in rateios_existentes and chave not in rateios_ja_adicionados:
                session.add(Rateio(
                    CHAPA=chapa,
                    RATEIO_FUNCIONARIO=dados["rateio_funcionario"],
                    GRPCCUSTO=dados["grpccusto"],
                ))
                rateios_ja_adicionados.add(chave)
                codigos_rateio_por_chapa.setdefault(chapa, []).append(
                    dados["rateio_funcionario"]
                )
                resumo["rateios_novos"] += 1
                resumo["detalhes_rateios"].append({
                    "chapa": chapa,
                    "nome": campos["NOME"] or "",
                    "rateio": dados["rateio_funcionario"],
                    "grpccusto": dados["grpccusto"] or "—",
                })

    # SEÇÃO_TRATADA e TIPO_CCUSTO por último, com TODOS os rateios de cada
    # colaborador já resolvidos (os que a planilha trouxe + os que já
    # existiam) — ver database/depara.py.
    for chapa in chapas_ja_contadas:
        colaborador = colaboradores_existentes[chapa]
        colaborador.SEÇÃO_TRATADA = secao_tratada(colaborador.SEÇÃO)
        colaborador.TIPO_CCUSTO = tipos_ccusto_dos_rateios(
            codigos_rateio_por_chapa.get(chapa, [])
        )

    return resumo


def importar_colaboradores():
    session = SessionLocal()

    try:
        resumo = processar_planilha_colaboradores(ARQUIVO_EXCEL, session, aplicar=True)
        session.commit()

        print("Importação concluída!")
        print(f"Novos colaboradores: {resumo['criados']}")
        print(f"Colaboradores atualizados: {resumo['atualizados']}")
        print(f"Novos rateios: {resumo['rateios_novos']}")
        if resumo["erros"]:
            print(f"Linhas com erro: {len(resumo['erros'])}")
            for erro in resumo["erros"]:
                print(f"  linha {erro['linha']}: {erro['erro']}")

    except Exception as erro:
        session.rollback()
        print(f"Erro durante a importação: {erro}")

    finally:
        session.close()


if __name__ == "__main__":
    importar_colaboradores()
