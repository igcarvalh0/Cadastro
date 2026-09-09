"""Regras de senha, niveis e vinculos. Nao tocam o banco."""

import pytest

import auth


# ============================================================
# SENHAS
# ============================================================

def test_senha_nao_e_guardada_em_texto():
    senha = "ABC98765"
    hash_gerado = auth.gerar_hash_senha(senha)

    assert senha not in hash_gerado
    assert hash_gerado.startswith("scrypt:")


def test_hash_e_diferente_a_cada_vez():
    """Mesmo com a mesma senha: o sal muda, entao dois usuarios com a mesma
    senha nao ficam com o mesmo hash no banco."""
    assert auth.gerar_hash_senha("mesmasenha") != auth.gerar_hash_senha("mesmasenha")


class UsuarioFalso:
    def __init__(self, senha):
        self.SENHA_HASH = auth.gerar_hash_senha(senha) if senha else None


def test_senha_confere_so_com_a_senha_certa():
    usuario = UsuarioFalso("segredo123")

    assert auth.senha_confere(usuario, "segredo123")
    assert not auth.senha_confere(usuario, "segredo124")
    assert not auth.senha_confere(usuario, "")
    assert not auth.senha_confere(None, "segredo123")
    assert not auth.senha_confere(UsuarioFalso(None), "segredo123")


@pytest.mark.parametrize(
    ("senha", "aceita"),
    [
        ("abc", False),
        ("12345", False),
        ("", False),
        (None, False),
        ("123456", True),
        ("ABC98765", True),
    ],
)
def test_tamanho_minimo_de_senha(senha, aceita):
    assert (auth.validar_senha(senha) is None) is aceita


# ============================================================
# NÍVEIS
# ============================================================

def test_mestre_tem_todas_as_permissoes():
    assert auth.permissoes_do_nivel(auth.NIVEL_MESTRE) == set(auth.TODAS_PERMISSOES)


def test_mestre_ignora_vinculos():
    assert auth.NIVEIS[auth.NIVEL_MESTRE]["ignora_vinculos"] is True


def test_nivel_desconhecido_nao_da_permissao_nenhuma():
    """Se um usuario ficar com um NIVEL que saiu da tabela, ele perde acesso
    em vez de herdar tudo."""
    assert auth.permissoes_do_nivel("NIVEL_QUE_NAO_EXISTE") == set()
    assert auth.permissoes_do_nivel(None) == set()


def test_todo_nivel_declara_permissoes_validas():
    for nome, dados in auth.NIVEIS.items():
        assert dados["permissoes"] <= set(auth.TODAS_PERMISSOES), nome
        assert dados["rotulo"], nome
        assert dados["descricao"], nome


# ============================================================
# VÍNCULOS
# ============================================================

class VinculosFalsos(list):
    """Imita a coleção do SQLAlchemy o suficiente para a funcao."""


class UsuarioComVinculos:
    def __init__(self):
        self.vinculos = VinculosFalsos()


class SessaoFalsa:
    def flush(self):
        pass


def vinculos_como_pares(usuario):
    return sorted((v.TIPO, v.VALOR) for v in usuario.vinculos)


def test_substituir_vinculos_guarda_os_tipos_conhecidos():
    usuario = UsuarioComVinculos()

    auth.substituir_vinculos(SessaoFalsa(), usuario, {
        "BASE": ["BACABAL", "PEDREIRAS"],
        "SETOR": ["Setor Leste"],
    })

    assert vinculos_como_pares(usuario) == [
        ("BASE", "BACABAL"),
        ("BASE", "PEDREIRAS"),
        ("SETOR", "Setor Leste"),
    ]


def test_substituir_vinculos_descarta_lixo():
    usuario = UsuarioComVinculos()

    auth.substituir_vinculos(SessaoFalsa(), usuario, {
        "BASE": ["BACABAL", "  ", "", "BACABAL", "  PEDREIRAS  "],
        "TIPO_INVENTADO": ["nao entra"],
    })

    # sem repetidos, sem vazios, com espacos aparados e sem o tipo desconhecido
    assert vinculos_como_pares(usuario) == [
        ("BASE", "BACABAL"),
        ("BASE", "PEDREIRAS"),
    ]


def test_substituir_vinculos_troca_os_antigos():
    usuario = UsuarioComVinculos()

    auth.substituir_vinculos(SessaoFalsa(), usuario, {"BASE": ["BACABAL"]})
    auth.substituir_vinculos(SessaoFalsa(), usuario, {"SETOR": ["Setor Novo"]})

    assert vinculos_como_pares(usuario) == [("SETOR", "Setor Novo")]


def test_sem_vinculos_nao_quebra():
    usuario = UsuarioComVinculos()

    auth.substituir_vinculos(SessaoFalsa(), usuario, None)
    auth.substituir_vinculos(SessaoFalsa(), usuario, {})

    assert vinculos_como_pares(usuario) == []
