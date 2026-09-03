import pytest

from app import base_da_secao, normalizar


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
