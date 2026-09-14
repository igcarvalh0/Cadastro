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

def test_administrador_tem_todas_as_permissoes():
    assert auth.permissoes_do_nivel(auth.NIVEL_ADMINISTRADOR) == set(auth.TODAS_PERMISSOES)


def test_administrador_ignora_vinculos():
    assert auth.NIVEIS[auth.NIVEL_ADMINISTRADOR]["ignora_vinculos"] is True


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


def test_supervisor_nao_ignora_vinculos():
    assert auth.NIVEIS[auth.NIVEL_SUPERVISOR]["ignora_vinculos"] is False


def test_supervisor_pode_alocar_mas_nao_gerenciar_usuarios():
    permissoes = auth.NIVEIS[auth.NIVEL_SUPERVISOR]["permissoes"]
    assert auth.ALOCAR in permissoes
    assert auth.GERENCIAR_USUARIOS not in permissoes


# ============================================================
# ESCOPO DE BASE E TIPO DE EQUIPE
# ============================================================

def test_administrador_pode_atuar_em_qualquer_base_e_tipo():
    administrador = {"ignora_vinculos": True, "vinculos": {}}
    assert auth.pode_atuar_na_base_e_tipo(administrador, "BACABAL", "PODA") is True


def test_sem_usuario_nao_pode_atuar():
    assert auth.pode_atuar_na_base_e_tipo(None, "BACABAL", "PODA") is False


def test_supervisor_so_atua_onde_tem_os_dois_vinculos():
    supervisor = {
        "ignora_vinculos": False,
        "vinculos": {
            auth.VINCULO_BASE: ["BACABAL"],
            auth.VINCULO_TIPO_EQUIPE: ["PODA"],
        },
    }

    assert auth.pode_atuar_na_base_e_tipo(supervisor, "BACABAL", "PODA") is True
    # base bate, mas o tipo nao esta entre os vinculados
    assert auth.pode_atuar_na_base_e_tipo(supervisor, "BACABAL", "CONSTRUÇÃO") is False
    # tipo bate, mas a base nao esta entre as vinculadas
    assert auth.pode_atuar_na_base_e_tipo(supervisor, "SÃO LUÍS", "PODA") is False


def test_supervisor_sem_vinculos_nao_atua_em_nada():
    supervisor = {"ignora_vinculos": False, "vinculos": {}}
    assert auth.pode_atuar_na_base_e_tipo(supervisor, "BACABAL", "PODA") is False


def test_setor_e_equipe_nao_restringem_quando_ausentes():
    """Quem so usa BASE+TIPO_EQUIPE continua funcionando igual, mesmo com
    SETOR/EQUIPE existindo como vinculo possivel para outros usuarios."""
    supervisor = {
        "ignora_vinculos": False,
        "vinculos": {
            auth.VINCULO_BASE: ["BACABAL"],
            auth.VINCULO_TIPO_EQUIPE: ["PODA"],
        },
    }

    assert auth.pode_atuar_na_base_e_tipo(
        supervisor, "BACABAL", "PODA", setor="Setor Leste", equipe_id=99
    ) is True
    assert auth.pode_atuar_na_base_e_tipo(supervisor, "BACABAL", "PODA") is True


def test_setor_restringe_quando_cadastrado():
    supervisor = {
        "ignora_vinculos": False,
        "vinculos": {
            auth.VINCULO_BASE: ["BACABAL"],
            auth.VINCULO_TIPO_EQUIPE: ["PODA"],
            auth.VINCULO_SETOR: ["Setor Leste"],
        },
    }

    assert auth.pode_atuar_na_base_e_tipo(
        supervisor, "BACABAL", "PODA", setor="Setor Leste"
    ) is True
    assert auth.pode_atuar_na_base_e_tipo(
        supervisor, "BACABAL", "PODA", setor="Setor Oeste"
    ) is False
    # base e tipo batem, mas sem setor nenhum informado tambem nao bate
    assert auth.pode_atuar_na_base_e_tipo(supervisor, "BACABAL", "PODA") is False


def test_equipe_especifica_restringe_quando_cadastrada():
    supervisor = {
        "ignora_vinculos": False,
        "vinculos": {
            auth.VINCULO_BASE: ["BACABAL"],
            auth.VINCULO_TIPO_EQUIPE: ["PODA"],
            auth.VINCULO_EQUIPE: ["12"],
        },
    }

    assert auth.pode_atuar_na_base_e_tipo(
        supervisor, "BACABAL", "PODA", equipe_id=12
    ) is True
    assert auth.pode_atuar_na_base_e_tipo(
        supervisor, "BACABAL", "PODA", equipe_id=13
    ) is False


def test_coordenador_nao_cruza_vinculo_de_supervisores_diferentes():
    """Caso real da RAFAELA: um Supervisor cobre PRES DUTRA/CONSTRUÇÃO e o
    outro BARRA DO CORDA/LINHA VIVA. Ela herda os dois escopos, mas nao a
    combinacao BARRA DO CORDA + CONSTRUÇÃO, que nao e de ninguem.
    """
    coordenadora = {
        "ignora_vinculos": False,
        "escopos": [
            {
                auth.VINCULO_BASE: ["PRES DUTRA"],
                auth.VINCULO_TIPO_EQUIPE: ["CONSTRUÇÃO"],
            },
            {
                auth.VINCULO_BASE: ["BARRA DO CORDA"],
                auth.VINCULO_TIPO_EQUIPE: ["LINHA VIVA"],
            },
        ],
        # a soma, que a tela exibe, nao pode mandar na checagem
        "vinculos": {
            auth.VINCULO_BASE: ["BARRA DO CORDA", "PRES DUTRA"],
            auth.VINCULO_TIPO_EQUIPE: ["CONSTRUÇÃO", "LINHA VIVA"],
        },
    }

    assert auth.pode_atuar_na_base_e_tipo(
        coordenadora, "PRES DUTRA", "CONSTRUÇÃO"
    ) is True
    assert auth.pode_atuar_na_base_e_tipo(
        coordenadora, "BARRA DO CORDA", "LINHA VIVA"
    ) is True
    assert auth.pode_atuar_na_base_e_tipo(
        coordenadora, "BARRA DO CORDA", "CONSTRUÇÃO"
    ) is False


def test_escopo_de_subordinado_sem_vinculo_nao_vira_curinga():
    coordenador = {
        "ignora_vinculos": False,
        "escopos": [{}, {auth.VINCULO_BASE: ["BACABAL"]}],
    }

    assert auth.pode_atuar_na_base_e_tipo(coordenador, "BACABAL", "PODA") is True
    assert auth.pode_atuar_na_base_e_tipo(coordenador, "SÃO LUÍS", "PODA") is False


# ============================================================
# VISIBILIDADE DE EQUIPE
# ============================================================

def test_equipe_visivel_basta_uma_vaga_bater():
    supervisor = {
        "ignora_vinculos": False,
        "vinculos": {
            auth.VINCULO_BASE: ["BACABAL"],
            auth.VINCULO_TIPO_EQUIPE: ["PODA"],
        },
    }

    pares = [("CONSTRUÇÃO", "Setor Oeste"), ("PODA", "Setor Leste")]
    assert auth.equipe_visivel(supervisor, "BACABAL", pares) is True


def test_equipe_visivel_respeita_setor_cadastrado():
    supervisor = {
        "ignora_vinculos": False,
        "vinculos": {
            auth.VINCULO_BASE: ["BACABAL"],
            auth.VINCULO_TIPO_EQUIPE: ["PODA"],
            auth.VINCULO_SETOR: ["Setor Leste"],
        },
    }

    # so tem vaga de Poda no Setor Oeste: nao bate
    assert auth.equipe_visivel(supervisor, "BACABAL", [("PODA", "Setor Oeste")]) is False
    assert auth.equipe_visivel(supervisor, "BACABAL", [("PODA", "Setor Leste")]) is True


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
        "TIPO_EQUIPE": ["PODA"],
    })

    assert vinculos_como_pares(usuario) == [
        ("BASE", "BACABAL"),
        ("BASE", "PEDREIRAS"),
        ("TIPO_EQUIPE", "PODA"),
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
    auth.substituir_vinculos(SessaoFalsa(), usuario, {"TIPO_EQUIPE": ["PODA"]})

    assert vinculos_como_pares(usuario) == [("TIPO_EQUIPE", "PODA")]


def test_sem_vinculos_nao_quebra():
    usuario = UsuarioComVinculos()

    auth.substituir_vinculos(SessaoFalsa(), usuario, None)
    auth.substituir_vinculos(SessaoFalsa(), usuario, {})

    assert vinculos_como_pares(usuario) == []
