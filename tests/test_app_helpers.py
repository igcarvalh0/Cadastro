import pytest

from app import base_da_secao, normalizar, padronizar_funcao


@pytest.mark.parametrize(
    ("secao", "base", "codigo"),
    [
        ("CT 127 - SETOR BACABAL", "BACABAL", "BCB"),
        ("CT 169 - SETOR PRESIDENTE DUTRA", "PRESIDENTE DUTRA", "PDT"),
        ("CT 127 - SETOR DE ITAPECURU MIRIM", "ITAPECURU MIRIM", "ITM"),
        ("CT 170 - SETOR DE BARRA DO CORDA", "BARRA DO CORDA", "BDC"),
    ],
)
def test_base_da_secao_aplica_de_para(secao, base, codigo):
    assert base_da_secao(secao) == {"nome": base, "codigo": codigo}


def test_normalizar_remove_acentos_e_padroniza():
    assert normalizar("Santa Inês") == "SANTA INES"


@pytest.mark.parametrize(
    ("cadastro", "categoria"),
    [
        # variacoes que o cadastro traz e precisam cair na mesma categoria
        ("MOTORISTA OP DE GUINCHO", "MOTORISTA"),
        ("Munqueiro/Motorista", "MOTORISTA"),
        ("ENCARREGADO OPERACIONAL", "ENCARREGADO"),
        ("ENCARREGADO OPERACIONAL II", "ENCARREGADO"),
        ("ENCARREGADO DE PODA", "ENCARREGADO"),
        ("ENCARREGADO LINHA VIVA DE DISTRIBUICAO", "ENCARREGADO"),
        ("ELETRICISTA MONTADOR", "ELETRICISTA"),
        ("ELETRICISTA LINHA VIVA DE DISTRIBUICAO", "ELETRICISTA"),
        ("Podador", "PODADOR"),
        ("Auxiliar de Eletricista", "AUXILIAR DE ELETRICISTA"),
        # nao sao auxiliar de eletricista: precisam das duas palavras
        ("AUXILIAR ADMINISTRATIVO", "AUXILIAR ADMINISTRATIVO"),
        ("AUXILIAR DE ALMOXARIFADO", "AUXILIAR DE ALMOXARIFADO"),
        ("AUXILIAR SERVICOS GERAIS", "AUXILIAR SERVICOS GERAIS"),
    ],
)
def test_padronizar_funcao_agrupa_por_palavra(cadastro, categoria):
    assert padronizar_funcao(cadastro) == categoria


def test_padronizar_funcao_ignora_vazio():
    assert padronizar_funcao(None) == ""
    assert padronizar_funcao("   ") == ""
