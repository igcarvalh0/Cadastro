"""Recalcula SEÇÃO_TRATADA e TIPO_CCUSTO de TODOS os colaboradores já
cadastrados, a partir do de-para em database/depara.py.

Uma nova importação da planilha de colaboradores já recalcula esses campos
sozinha (ver database/importacao/importar_colaboradores.py), então este
script só é necessário:
- uma vez, para preencher os colaboradores que já existiam antes da coluna
  existir (rode logo depois de aplicar a migration 010);
- de novo, se o de-para em depara_cadastro.json for atualizado no futuro
  (um código ou seção novos, por exemplo) e for preciso re-aplicar a
  tradução em quem já está cadastrado.

Uso:
    python -m database.importacao.recalcular_secao_tipo_ccusto
"""
from collections import defaultdict

from database.database import SessionLocal
from database.depara import secao_tratada, tipos_ccusto_dos_rateios
from database.models import Colaborador, Rateio


def recalcular():
    session = SessionLocal()
    try:
        codigos_por_chapa = defaultdict(list)
        for chapa, codigo in session.query(Rateio.CHAPA, Rateio.RATEIO_FUNCIONARIO):
            if codigo:
                codigos_por_chapa[chapa].append(codigo)

        colaboradores = session.query(Colaborador).all()
        alterados = 0
        for colaborador in colaboradores:
            nova_secao = secao_tratada(colaborador.SEÇÃO)
            novo_ccusto = tipos_ccusto_dos_rateios(codigos_por_chapa.get(colaborador.CHAPA, []))
            if colaborador.SEÇÃO_TRATADA != nova_secao or colaborador.TIPO_CCUSTO != novo_ccusto:
                colaborador.SEÇÃO_TRATADA = nova_secao
                colaborador.TIPO_CCUSTO = novo_ccusto
                alterados += 1

        session.commit()
        print(f"Recalculado: {len(colaboradores)} colaboradores conferidos, {alterados} atualizados.")
    except Exception as erro:
        session.rollback()
        print(f"Erro ao recalcular: {erro}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    recalcular()
