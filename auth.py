"""Login, niveis de acesso e vinculos.

Separado do app.py para deixar claro o que e regra de permissao e o que e
regra de negocio das equipes.

COMO FUNCIONA
-------------
- Cada usuario tem um NIVEL, e o nivel e um conjunto de PERMISSOES.
  Quem pode o que esta em NIVEIS, logo abaixo — e o unico lugar a mexer
  para criar ou alterar um nivel.
- Alem do nivel, o usuario tem VINCULOS: pares TIPO/VALOR que dizem sobre
  QUAIS equipes ele age (base, setor, supervisor ou coordenador). Nivel diz
  "o que pode fazer"; vinculo diz "com quais dados".
- MESTRE ignora vinculos: enxerga tudo.
"""

from functools import wraps

from flask import g, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash

from database.database import SessionLocal
from database.models import Usuario, VinculoUsuario


# ============================================================
# PERMISSÕES
# ============================================================

# Cada permissao e uma acao que a tela oferece. Para criar um nivel novo,
# monte uma combinacao destas em NIVEIS.
VER_RESUMO = "ver_resumo"
VER_EQUIPES = "ver_equipes"
ALOCAR = "alocar"                 # colocar e tirar colaborador de vaga
GERENCIAR_VAGAS = "gerenciar_vagas"   # criar/editar equipes e vagas, planilha
GERENCIAR_USUARIOS = "gerenciar_usuarios"

TODAS_PERMISSOES = (
    VER_RESUMO,
    VER_EQUIPES,
    ALOCAR,
    GERENCIAR_VAGAS,
    GERENCIAR_USUARIOS,
)

NIVEL_MESTRE = "MESTRE"

# ------------------------------------------------------------
# NIVEIS
# ------------------------------------------------------------
# Só MESTRE está definido por enquanto. Os demais niveis entram aqui quando
# as regras forem definidas: basta uma linha nova com o nome e a lista de
# permissoes. A tela de usuarios le esta tabela, entao um nivel novo aparece
# no formulario sem precisar mexer no frontend.
NIVEIS = {
    NIVEL_MESTRE: {
        "rotulo": "Mestre",
        "descricao": "Acesso total, inclusive ao cadastro de usuários.",
        "permissoes": set(TODAS_PERMISSOES),
        "ignora_vinculos": True,
    },
}


# ============================================================
# VÍNCULOS
# ============================================================

VINCULO_BASE = "BASE"
VINCULO_SETOR = "SETOR"
VINCULO_SUPERVISOR = "SUPERVISOR"
VINCULO_COORDENADOR = "COORDENADOR"

TIPOS_VINCULO = {
    VINCULO_BASE: "Base",
    VINCULO_SETOR: "Setor",
    VINCULO_SUPERVISOR: "Supervisor",
    VINCULO_COORDENADOR: "Coordenador",
}


# ============================================================
# SENHAS
# ============================================================

def gerar_hash_senha(senha):
    """A senha nunca e guardada: so este hash vai para o banco."""
    return generate_password_hash(senha)


def senha_confere(usuario, senha):
    if not usuario or not usuario.SENHA_HASH:
        return False
    return check_password_hash(usuario.SENHA_HASH, senha)


SENHA_MINIMA = 6


def validar_senha(senha):
    """Devolve a mensagem de erro, ou None se a senha serve."""
    if not senha or len(senha) < SENHA_MINIMA:
        return f"A senha precisa de pelo menos {SENHA_MINIMA} caracteres."
    return None


# ============================================================
# SESSÃO
# ============================================================

CHAVE_SESSAO = "usuario_id"


def registrar_login(usuario):
    session.clear()
    session[CHAVE_SESSAO] = usuario.id
    session.permanent = True


def encerrar_sessao():
    session.clear()


def usuario_logado():
    """Usuario da requisicao atual, ou None. Fica em cache no g."""
    if "usuario_atual" in g:
        return g.usuario_atual

    g.usuario_atual = None
    usuario_id = session.get(CHAVE_SESSAO)

    if usuario_id is not None:
        sessao_banco = SessionLocal()
        try:
            usuario = (
                sessao_banco.query(Usuario)
                .filter(Usuario.id == usuario_id)
                .first()
            )
            # usuario apagado ou desativado depois de entrar perde o acesso
            if usuario and usuario.ATIVO:
                g.usuario_atual = descrever_usuario(usuario)
        finally:
            sessao_banco.close()

    return g.usuario_atual


def permissoes_do_nivel(nivel):
    return set(NIVEIS.get(nivel, {}).get("permissoes", ()))


def descrever_usuario(usuario, incluir_vinculos=True):
    """Formato que vai para a tela e para as checagens de permissao."""
    dados = {
        "id": usuario.id,
        "usuario": usuario.USUARIO,
        "nome": usuario.NOME,
        "nivel": usuario.NIVEL,
        "nivel_rotulo": NIVEIS.get(usuario.NIVEL, {}).get("rotulo", usuario.NIVEL),
        "ativo": bool(usuario.ATIVO),
        "permissoes": sorted(permissoes_do_nivel(usuario.NIVEL)),
        "ignora_vinculos": bool(
            NIVEIS.get(usuario.NIVEL, {}).get("ignora_vinculos", False)
        ),
    }

    if incluir_vinculos:
        vinculos = {}
        for vinculo in usuario.vinculos:
            vinculos.setdefault(vinculo.TIPO, []).append(vinculo.VALOR)
        dados["vinculos"] = {tipo: sorted(v) for tipo, v in vinculos.items()}

    return dados


def tem_permissao(permissao, usuario=None):
    usuario = usuario or usuario_logado()
    return bool(usuario) and permissao in usuario["permissoes"]


# ============================================================
# GUARDAS DE ROTA
# ============================================================

def exige_login(funcao):
    @wraps(funcao)
    def protegida(*args, **kwargs):
        if not usuario_logado():
            return jsonify({"erro": "Faça login para continuar."}), 401
        return funcao(*args, **kwargs)

    return protegida


def exige_permissao(permissao):
    def decorador(funcao):
        @wraps(funcao)
        def protegida(*args, **kwargs):
            usuario = usuario_logado()

            if not usuario:
                return jsonify({"erro": "Faça login para continuar."}), 401

            if permissao not in usuario["permissoes"]:
                return jsonify(
                    {"erro": "Seu nível de acesso não permite esta ação."}
                ), 403

            return funcao(*args, **kwargs)

        return protegida

    return decorador


# ============================================================
# APLICAR VÍNCULOS
# ============================================================

def substituir_vinculos(sessao_banco, usuario, vinculos):
    """Troca os vinculos do usuario pelos informados.

    'vinculos' e um dicionario {TIPO: [valores]}. Tipos desconhecidos e
    valores em branco sao descartados em silencio.
    """
    usuario.vinculos.clear()
    sessao_banco.flush()

    for tipo, valores in (vinculos or {}).items():
        if tipo not in TIPOS_VINCULO:
            continue

        for valor in dict.fromkeys(valores or []):
            texto = str(valor).strip()

            if texto:
                usuario.vinculos.append(
                    VinculoUsuario(TIPO=tipo, VALOR=texto)
                )
