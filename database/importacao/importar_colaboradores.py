import pandas as pd
from pathlib import Path

from database.database import SessionLocal
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

    resumo = {"criados": 0, "atualizados": 0, "rateios_novos": 0, "erros": []}

    linhas_validas = []
    for indice, linha in df.iterrows():
        numero = int(indice) + 2
        dados, erro = normalizar_linha_colaborador(linha)
        if erro:
            resumo["erros"].append({"linha": numero, "erro": erro})
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

    chapas_ja_contadas = set()
    rateios_ja_adicionados = set()

    for dados in linhas_validas:
        chapa = dados["chapa"]
        campos = {
            campo: dados[campo]
            for campo in ("NOME", "FUNÇÃO", "ADMISSÃO", "SEÇÃO", "SITUAÇÃO")
        }

        colaborador = colaboradores_existentes.get(chapa)
        if colaborador:
            for campo, valor in campos.items():
                setattr(colaborador, campo, valor)
            if chapa not in chapas_ja_contadas:
                resumo["atualizados"] += 1
        else:
            colaborador = Colaborador(CHAPA=chapa, **campos)
            session.add(colaborador)
            colaboradores_existentes[chapa] = colaborador
            if chapa not in chapas_ja_contadas:
                resumo["criados"] += 1

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
                resumo["rateios_novos"] += 1

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
