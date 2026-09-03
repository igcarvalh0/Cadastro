import pandas as pd
from pathlib import Path

from database.database import SessionLocal
from database.models import Colaborador, Rateio


ARQUIVO_EXCEL = Path(__file__).resolve().parent / "cadastro.xlsx"


def importar_colaboradores():
    df = pd.read_excel(ARQUIVO_EXCEL)

    session = SessionLocal()

    try:
        importados = 0
        atualizados = 0
        rateios_importados = 0

        # Remove linhas sem CHAPA
        df = df.dropna(subset=["CHAPA"])

        # Percorre cada linha do Excel
        for _, linha in df.iterrows():

            chapa = str(linha["CHAPA"]).strip()

            # Remove o ".0" que o Excel adicionou aos números
            if chapa.endswith(".0"):
                chapa = chapa[:-2]

            # Procura o colaborador
            colaborador = (
                session.query(Colaborador)
                .filter(Colaborador.CHAPA == chapa)
                .first()
            )

            # Converte a data de admissão
            admissao = pd.to_datetime(
                linha["ADMISSÃO"],
                dayfirst=True,
                errors="coerce"
            )

            if pd.isna(admissao):
                admissao = None
            else:
                admissao = admissao.date()

            # Dados principais do colaborador
            dados_colaborador = {
                "NOME": linha["NOME"],
                "FUNÇÃO": linha["FUNÇÃO"],
                "ADMISSÃO": admissao,
                "SEÇÃO": linha["SEÇÃO"],
                "SITUAÇÃO": linha["SITUAÇÃO"],
            }

            # Cria ou atualiza o colaborador
            if colaborador:
                for campo, valor in dados_colaborador.items():
                    setattr(colaborador, campo, valor)

                atualizados += 1

            else:
                colaborador = Colaborador(
                    CHAPA=chapa,
                    **dados_colaborador
                )

                session.add(colaborador)
                session.flush()

                importados += 1

            # Dados do rateio
            rateio_funcionario = linha["RATEIO_FUNCIONARIO"]
            grpccusto = linha["GRPCCUSTO"]

            # Ignora rateio vazio
            if pd.isna(rateio_funcionario):
                continue

            rateio_funcionario = str(rateio_funcionario).strip()

            if pd.isna(grpccusto):
                grpccusto = None
            else:
                grpccusto = str(grpccusto).strip()

            # Verifica se esse rateio já existe
            rateio_existente = (
                session.query(Rateio)
                .filter(
                    Rateio.CHAPA == chapa,
                    Rateio.RATEIO_FUNCIONARIO == rateio_funcionario,
                    Rateio.GRPCCUSTO == grpccusto
                )
                .first()
            )

            # Cria somente se ainda não existir
            if not rateio_existente:
                rateio = Rateio(
                    CHAPA=chapa,
                    RATEIO_FUNCIONARIO=rateio_funcionario,
                    GRPCCUSTO=grpccusto
                )

                session.add(rateio)
                rateios_importados += 1

        session.commit()

        print("Importação concluída!")
        print(f"Novos colaboradores: {importados}")
        print(f"Colaboradores atualizados: {atualizados}")
        print(f"Novos rateios: {rateios_importados}")

    except Exception as erro:
        session.rollback()
        print(f"Erro durante a importação: {erro}")

    finally:
        session.close()


if __name__ == "__main__":
    importar_colaboradores()

