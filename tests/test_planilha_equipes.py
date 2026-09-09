"""Regras da planilha de equipes, exercitadas sem tocar no banco.

A analise so precisa que a sessao devolva as equipes existentes, entao aqui ela
e substituida por objetos de mentira. Assim estes testes rodam mesmo com o .env
apontando para producao.
"""

import io

import pandas as pd
import pytest

from app import analisar_planilha_equipes

FIXAS = ["BASE", "PREFIXO", "TIPO EQUIPE", "SETOR", "SUPERVISOR", "COORDENADOR", "AÇÃO"]


class VagaFalsa:
    def __init__(self, id, funcao, tipo, setor=None, supervisor=None,
                 coordenador=None, ocupada=False):
        self.id = id
        self.FUNÇÃO_ER = funcao
        self.ESTRUTURA = tipo
        self.SETOR = setor
        self.SUPERVISOR = supervisor
        self.COORDENADOR = coordenador
        self.membro = object() if ocupada else None


class EquipeFalsa:
    def __init__(self, id, base, prefixo, composicoes):
        self.id = id
        self.BASE = base
        self.PREFIXO = prefixo
        self.composicoes = composicoes


class SessaoFalsa:
    """Responde apenas ao query(...).options(...).all() que a analise usa."""

    def __init__(self, equipes):
        self._equipes = equipes

    def query(self, *_):
        return self

    def options(self, *_):
        return self

    def all(self):
        return self._equipes


def planilha(linhas, funcoes=("Eletricista",)):
    dados = []
    for linha in linhas:
        registro = {coluna: linha.get(coluna, "") for coluna in FIXAS}
        for funcao in funcoes:
            registro[funcao] = linha.get(funcao, 0)
        dados.append(registro)

    arquivo = io.BytesIO()
    with pd.ExcelWriter(arquivo, engine="openpyxl") as writer:
        pd.DataFrame(dados, columns=FIXAS + list(funcoes)).to_excel(
            writer, index=False, sheet_name="Equipes"
        )
    arquivo.seek(0)
    return arquivo


def equipe_com(vagas, base="BCB", prefixo="EQ-1"):
    return EquipeFalsa(1, base, prefixo, vagas)


def mudancas_de(plano):
    assert not plano["erros"], plano["erros"]
    assert len(plano["editar"]) == 1, plano
    return plano["editar"][0]["mudancas"]


def test_troca_de_responsavel_junto_com_quantidade_alcanca_as_vagas_antigas():
    """Regressao: mudar SUPERVISOR e quantidade na mesma linha deixava as vagas
    ja existentes com o responsavel velho, e a previa nao avisava nada."""
    existentes = [
        VagaFalsa(10, "Eletricista", "CONSTRUÇÃO", supervisor="ANTIGO"),
        VagaFalsa(11, "Eletricista", "CONSTRUÇÃO", supervisor="ANTIGO"),
    ]
    sessao = SessaoFalsa([equipe_com(existentes)])

    plano = analisar_planilha_equipes(
        planilha([{
            "BASE": "BCB", "PREFIXO": "EQ-1", "TIPO EQUIPE": "CONSTRUÇÃO",
            "SUPERVISOR": "NOVO", "AÇÃO": "editar", "Eletricista": 3,
        }]),
        sessao,
    )

    mudancas = mudancas_de(plano)
    atualizacao = next(m for m in mudancas if "atualizar_metadados" in m)

    assert sorted(atualizacao["ids"]) == [10, 11]
    assert atualizacao["supervisor"] == "NOVO"
    assert any(m.get("adicionar") == 1 for m in mudancas)
    # a previa precisa dizer que o responsavel muda, senao a troca some calada
    assert "responsável" in plano["editar"][0]["resumo"]


def test_vaga_que_sai_da_disciplina_nao_recebe_o_responsavel_da_origem():
    """Quem e retipado leva o responsavel do destino, nao o da disciplina antiga."""
    existentes = [
        VagaFalsa(20, "Eletricista", "CONSTRUÇÃO", supervisor="ANTIGO"),
        VagaFalsa(21, "Eletricista", "CONSTRUÇÃO", supervisor="ANTIGO"),
    ]
    sessao = SessaoFalsa([equipe_com(existentes)])

    plano = analisar_planilha_equipes(
        planilha([{
            "BASE": "BCB", "PREFIXO": "EQ-1", "TIPO EQUIPE": "PODA",
            "SUPERVISOR": "DA PODA", "AÇÃO": "editar", "Eletricista": 2,
        }]),
        sessao,
    )

    mudancas = mudancas_de(plano)
    retipagem = next(m for m in mudancas if "retipar" in m)

    assert retipagem["de"] == "CONSTRUÇÃO"
    assert retipagem["para"] == "PODA"
    assert retipagem["supervisor"] == "DA PODA"
    # nada sobrou em CONSTRUÇÃO, entao nao ha metadado a atualizar por la
    assert not [m for m in mudancas if "atualizar_metadados" in m]


def test_sem_mudanca_nenhuma_a_linha_e_ignorada():
    existentes = [VagaFalsa(30, "Eletricista", "CONSTRUÇÃO", supervisor="MESMO")]
    sessao = SessaoFalsa([equipe_com(existentes)])

    plano = analisar_planilha_equipes(
        planilha([{
            "BASE": "BCB", "PREFIXO": "EQ-1", "TIPO EQUIPE": "CONSTRUÇÃO",
            "SUPERVISOR": "MESMO", "AÇÃO": "editar", "Eletricista": 1,
        }]),
        sessao,
    )

    assert plano["editar"] == []
    assert plano["ignoradas"] == 1


def test_nao_apaga_vaga_ocupada_para_diminuir_quantidade():
    existentes = [
        VagaFalsa(40, "Eletricista", "CONSTRUÇÃO", ocupada=True),
        VagaFalsa(41, "Eletricista", "CONSTRUÇÃO", ocupada=True),
    ]
    sessao = SessaoFalsa([equipe_com(existentes)])

    plano = analisar_planilha_equipes(
        planilha([{
            "BASE": "BCB", "PREFIXO": "EQ-1", "TIPO EQUIPE": "CONSTRUÇÃO",
            "AÇÃO": "editar", "Eletricista": 0,
        }]),
        sessao,
    )

    assert plano["erros"]
    assert "Remova os colaboradores antes" in plano["erros"][0]["erro"]


@pytest.mark.parametrize(
    ("acao", "mensagem"),
    [("apagar", "não existe"), ("", None)],
)
def test_acao_invalida_ou_vazia(acao, mensagem):
    sessao = SessaoFalsa([])
    plano = analisar_planilha_equipes(
        planilha([{
            "BASE": "BCB", "PREFIXO": "EQ-9", "TIPO EQUIPE": "CONSTRUÇÃO",
            "AÇÃO": acao, "Eletricista": 1,
        }]),
        sessao,
    )

    if mensagem:
        assert mensagem in plano["erros"][0]["erro"]
    else:
        # linha sem acao nao e erro: e so ignorada
        assert not plano["erros"]
        assert plano["ignoradas"] == 1


def test_quantidade_nao_numerica_vira_erro_de_linha():
    sessao = SessaoFalsa([])
    plano = analisar_planilha_equipes(
        planilha([{
            "BASE": "BCB", "PREFIXO": "EQ-9", "TIPO EQUIPE": "CONSTRUÇÃO",
            "AÇÃO": "criar", "Eletricista": "duas",
        }]),
        sessao,
    )

    assert "números inteiros" in plano["erros"][0]["erro"]


def test_planilha_sem_coluna_obrigatoria():
    arquivo = io.BytesIO()
    with pd.ExcelWriter(arquivo, engine="openpyxl") as writer:
        pd.DataFrame([{"BASE": "BCB", "Eletricista": 1}]).to_excel(
            writer, index=False, sheet_name="Equipes"
        )
    arquivo.seek(0)

    with pytest.raises(ValueError, match="PREFIXO"):
        analisar_planilha_equipes(arquivo, SessaoFalsa([]))
