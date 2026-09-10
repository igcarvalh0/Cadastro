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


def aplicar_linha_colaborador(session, dados):
    """Upsert do colaborador por CHAPA + rateio (append-only, idempotente por
    combinação exata CHAPA+RATEIO_FUNCIONARIO+GRPCCUSTO). Devolve
    (resultado, novo_rateio) onde resultado é 'criado' ou 'atualizado'."""
    colaborador = (
        session.query(Colaborador).filter(Colaborador.CHAPA == dados["chapa"]).first()
    )
    campos = {
        campo: dados[campo]
        for campo in ("NOME", "FUNÇÃO", "ADMISSÃO", "SEÇÃO", "SITUAÇÃO")
    }

    if colaborador:
        for campo, valor in campos.items():
            setattr(colaborador, campo, valor)
        resultado = "atualizado"
    else:
        colaborador = Colaborador(CHAPA=dados["chapa"], **campos)
        session.add(colaborador)
        session.flush()
        resultado = "criado"

    novo_rateio = False
    if dados["rateio_funcionario"]:
        existente = (
            session.query(Rateio)
            .filter(
                Rateio.CHAPA == dados["chapa"],
                Rateio.RATEIO_FUNCIONARIO == dados["rateio_funcionario"],
                Rateio.GRPCCUSTO == dados["grpccusto"],
            )
            .first()
        )
        if not existente:
            session.add(Rateio(
                CHAPA=dados["chapa"],
                RATEIO_FUNCIONARIO=dados["rateio_funcionario"],
                GRPCCUSTO=dados["grpccusto"],
            ))
            novo_rateio = True

    return resultado, novo_rateio


def processar_planilha_colaboradores(arquivo, session, aplicar):
    """Le a planilha inteira e aplica linha a linha na sessao dada.

    aplicar=False roda a mesma lógica de upsert mas o chamador é quem decide
    se comita ou dá rollback (usado para gerar uma prévia sem gravar nada).
    Devolve um resumo com contagens e erros por linha.
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

    for indice, linha in df.iterrows():
        numero = int(indice) + 2
        dados, erro = normalizar_linha_colaborador(linha)
        if erro:
            resumo["erros"].append({"linha": numero, "erro": erro})
            continue

        resultado, novo_rateio = aplicar_linha_colaborador(session, dados)
        if resultado == "criado":
            resumo["criados"] += 1
        else:
            resumo["atualizados"] += 1
        if novo_rateio:
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
