import pandas as pd
from pathlib import Path

from database.database import SessionLocal
from database.models import Equipe, ComposicaoEquipe


ARQUIVO_EXCEL = Path(__file__).resolve().parent / "equipes.xlsx"


def importar_equipes():

    df = pd.read_excel(ARQUIVO_EXCEL)

    print("Colunas encontradas no Excel:")
    print(df.columns.tolist())

    session = SessionLocal()

    try:

        equipes_criadas = 0
        composicoes_criadas = 0

        for _, linha in df.iterrows():

            # ====================================================
            # IGNORA LINHAS COMPLETAMENTE VAZIAS
            # ====================================================

            if linha.isna().all():
                continue


            # ====================================================
            # LER DADOS DO EXCEL
            # ====================================================

            base = str(
                linha["BASE"]
            ).strip()

            funcao_er = str(
                linha["FUNÇÃO ER"]
            ).strip()

            prefixo = str(
                linha["PREFIXO"]
            ).strip()

            estrutura = str(
                linha["ESTRUTURA"]
            ).strip()


            # ====================================================
            # IGNORA LINHAS SEM PREFIXO
            # ====================================================

            if (
                not prefixo
                or prefixo.lower() == "nan"
            ):
                continue


            # ====================================================
            # PROCURA A EQUIPE
            #
            # A IDENTIFICAÇÃO AGORA É:
            # BASE + PREFIXO
            #
            # Isso permite ter:
            #
            # BASE 01 | FOLGUISTA
            # BASE 02 | FOLGUISTA
            #
            # como equipes diferentes.
            # ====================================================

            equipe = (
                session.query(
                    Equipe
                )
                .filter(
                    Equipe.BASE == base,
                    Equipe.PREFIXO == prefixo
                )
                .first()
            )


            # ====================================================
            # SE NÃO EXISTIR, CRIA A EQUIPE
            # ====================================================

            if not equipe:

                equipe = Equipe(

                    BASE=base,

                    PREFIXO=prefixo

                )

                session.add(
                    equipe
                )

                session.flush()

                equipes_criadas += 1


            # ====================================================
            # VERIFICA SE A COMPOSIÇÃO JÁ EXISTE
            # ====================================================

            composicao = (
                session.query(
                    ComposicaoEquipe
                )
                .filter(
                    ComposicaoEquipe.equipe_id
                    == equipe.id,

                    ComposicaoEquipe.FUNÇÃO_ER
                    == funcao_er,

                    ComposicaoEquipe.ESTRUTURA
                    == estrutura
                )
                .first()
            )


            # ====================================================
            # SE NÃO EXISTIR, CRIA A COMPOSIÇÃO
            # ====================================================

            if not composicao:

                composicao = ComposicaoEquipe(

                    equipe_id=
                        equipe.id,

                    FUNÇÃO_ER=
                        funcao_er,

                    ESTRUTURA=
                        estrutura

                )

                session.add(
                    composicao
                )

                composicoes_criadas += 1


        # ========================================================
        # SALVAR
        # ========================================================

        session.commit()


        print()
        print(
            "Importação das equipes concluída!"
        )

        print(
            f"Equipes criadas: {equipes_criadas}"
        )

        print(
            f"Composições criadas: {composicoes_criadas}"
        )


    except Exception as erro:

        session.rollback()

        print()

        print(
            f"Erro durante a importação: {erro}"
        )


    finally:

        session.close()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    importar_equipes()