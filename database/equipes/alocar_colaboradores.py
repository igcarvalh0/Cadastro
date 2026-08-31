from database.database import SessionLocal
from database.models import Equipe, ComposicaoEquipe, MembroEquipe, Colaborador


def buscar_colaborador(termo):
    session = SessionLocal()

    try:
        termo = str(termo).strip()

        # Primeiro tenta encontrar pela CHAPA
        colaborador = (
            session.query(Colaborador)
            .filter(Colaborador.CHAPA == termo)
            .first()
        )

        if colaborador:
            return colaborador

        # Se não encontrou pela chapa, procura pelo nome
        colaborador = (
            session.query(Colaborador)
            .filter(Colaborador.NOME.ilike(f"%{termo}%"))
            .all()
        )

        return colaborador

    finally:
        session.close()


def alocar_colaborador(composicao_id, chapa):
    session = SessionLocal()

    try:
        # Busca a vaga
        composicao = (
            session.query(ComposicaoEquipe)
            .filter(ComposicaoEquipe.id == composicao_id)
            .first()
        )

        if not composicao:
            print("Vaga não encontrada.")
            return

        # Verifica se a vaga já está ocupada
        if composicao.membro:
            print("Essa vaga já está ocupada.")
            return

        # Busca o colaborador
        colaborador = (
            session.query(Colaborador)
            .filter(Colaborador.CHAPA == str(chapa).strip())
            .first()
        )

        if not colaborador:
            print("Colaborador não encontrado.")
            return

        # Verifica se o colaborador já está em alguma equipe
        membro_existente = (
            session.query(MembroEquipe)
            .filter(MembroEquipe.CHAPA == colaborador.CHAPA)
            .first()
        )

        if membro_existente:
            print("Esse colaborador já está alocado em uma equipe.")
            return

        # Cria a alocação
        membro = MembroEquipe(
            composicao_id=composicao.id,
            CHAPA=colaborador.CHAPA
        )

        session.add(membro)
        session.commit()

        print("Colaborador alocado com sucesso!")
        print(f"CHAPA: {colaborador.CHAPA}")
        print(f"NOME: {colaborador.NOME}")
        print(f"FUNÇÃO ER: {composicao.FUNÇÃO_ER}")
        print(f"ESTRUTURA: {composicao.ESTRUTURA}")

    except Exception as erro:
        session.rollback()
        print(f"Erro ao alocar colaborador: {erro}")

    finally:
        session.close()


def listar_equipe(prefixo):
    session = SessionLocal()

    try:
        equipe = (
            session.query(Equipe)
            .filter(Equipe.PREFIXO == prefixo)
            .first()
        )

        if not equipe:
            print("Equipe não encontrada.")
            return

        print()
        print(f"Equipe: {equipe.PREFIXO}")
        print(f"Base: {equipe.BASE}")
        print("-" * 50)

        for composicao in equipe.composicoes:

            if composicao.membro:
                nome = composicao.membro.colaborador.NOME
                chapa = composicao.membro.colaborador.CHAPA

                print(
                    f"{composicao.ESTRUTURA} "
                    f"→ {nome} ({chapa})"
                )

            else:
                print(
                    f"{composicao.ESTRUTURA} "
                    f"→ VAGA LIVRE"
                )

    finally:
        session.close()
