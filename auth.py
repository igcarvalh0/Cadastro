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
- ADMINISTRADOR ignora vinculos: enxerga tudo.
"""

from functools import wraps

from flask import g, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash

from database.database import SessionLocal
from database.models import NivelPermissao, Usuario, VinculoUsuario


# ============================================================
# PERMISSÕES
# ============================================================

# Cada permissao e uma acao que a tela oferece. Para criar um nivel novo,
# monte uma combinacao destas em NIVEIS.
VER_RESUMO = "ver_resumo"
VER_EQUIPES = "ver_equipes"
ALOCAR = "alocar"                 # colocar colaborador numa vaga
EDITAR_ALOCACAO = "editar_alocacao"    # trocar o colaborador de uma vaga ocupada
REMOVER_ALOCACAO = "remover_alocacao"  # tirar colaborador de uma vaga
GERENCIAR_VAGAS = "gerenciar_vagas"   # criar/editar equipes e vagas, planilha
GERENCIAR_USUARIOS = "gerenciar_usuarios"
GERENCIAR_COLABORADORES = "gerenciar_colaboradores"  # atualizar cadastro por planilha

TODAS_PERMISSOES = (
    VER_RESUMO,
    VER_EQUIPES,
    ALOCAR,
    EDITAR_ALOCACAO,
    REMOVER_ALOCACAO,
    GERENCIAR_VAGAS,
    GERENCIAR_USUARIOS,
    GERENCIAR_COLABORADORES,
)

NIVEL_ADMINISTRADOR = "ADMINISTRADOR"
NIVEL_SUPERVISOR = "SUPERVISOR"
NIVEL_ANALISTA = "ANALISTA"

# ------------------------------------------------------------
# NIVEIS
# ------------------------------------------------------------
# Os demais niveis entram aqui quando as regras forem definidas: basta uma
# linha nova com o nome e a lista de permissoes. A tela de usuarios le esta
# tabela, entao um nivel novo aparece no formulario sem precisar mexer no
# frontend.
#
# O nivel antigo "MESTRE" foi renomeado para "ADMINISTRADOR" (codigo e banco
# — ver migrations/006_renomear_mestre_para_administrador.sql). Nao existe
# mais nenhuma referencia a "mestre" no sistema, so historico em migrations
# antigas.
NIVEIS = {
    NIVEL_ADMINISTRADOR: {
        "rotulo": "Administrador",
        "descricao": "Acesso total, inclusive ao cadastro de usuários.",
        "permissoes": set(TODAS_PERMISSOES),
        "ignora_vinculos": True,
    },
    NIVEL_SUPERVISOR: {
        "rotulo": "Supervisor",
        "descricao": (
            "Visualiza o resumo e as equipes; aloca e remove colaboradores "
            "somente nas bases e nos tipos de equipe vinculados a ele."
        ),
        "permissoes": {VER_RESUMO, VER_EQUIPES, ALOCAR, REMOVER_ALOCACAO},
        "ignora_vinculos": False,
    },
    NIVEL_ANALISTA: {
        "rotulo": "Analista",
        "descricao": (
            "Visualiza o resumo e as equipes. Alocar, editar e remover só "
            "funcionam se a operação estiver marcada aqui E a equipe/base/"
            "setor estiver nos vínculos dele, no cadastro do usuário."
        ),
        "permissoes": {VER_RESUMO, VER_EQUIPES},
        "ignora_vinculos": False,
    },
}

# O Administrador sempre tem acesso total — nao pode ser personalizado pela
# tela de niveis (senao dá pra alguem se trancar fora do proprio sistema).
NIVEIS_PERMISSOES_FIXAS = {NIVEL_ADMINISTRADOR}


# ============================================================
# VÍNCULOS
# ============================================================

VINCULO_BASE = "BASE"
VINCULO_TIPO_EQUIPE = "TIPO_EQUIPE"
VINCULO_SETOR = "SETOR"
VINCULO_SUPERVISOR = "SUPERVISOR"
VINCULO_COORDENADOR = "COORDENADOR"
VINCULO_EQUIPE = "EQUIPE"          # id de uma equipe especifica (Analista)

TIPOS_VINCULO = {
    VINCULO_BASE: "Base",
    VINCULO_TIPO_EQUIPE: "Tipo de equipe",
    VINCULO_SETOR: "Setor",
    VINCULO_SUPERVISOR: "Supervisor",
    VINCULO_COORDENADOR: "Coordenador",
    VINCULO_EQUIPE: "Equipe específica",
}

# Identificadores de operacao usados por pode_realizar_operacao — nao sao
# vinculo (isso e "o que fazer", nao "sobre qual equipe"). O que cada nivel
# pode fazer e a PERMISSAO correspondente (ver PERMISSAO_POR_OPERACAO),
# editavel na tela de Usuarios > Niveis de acesso.
OPERACAO_ALOCAR = "ALOCAR"
OPERACAO_EDITAR = "EDITAR"
OPERACAO_REMOVER = "REMOVER"

PERMISSAO_POR_OPERACAO = {
    OPERACAO_ALOCAR: ALOCAR,
    OPERACAO_EDITAR: EDITAR_ALOCACAO,
    OPERACAO_REMOVER: REMOVER_ALOCACAO,
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
                g.usuario_atual = descrever_usuario(usuario, session=sessao_banco)
        finally:
            sessao_banco.close()

    return g.usuario_atual


def _permissoes_customizadas(session, nivel):
    """Permissoes gravadas na tela de niveis para este nivel, ou None se ele
    nunca foi personalizado (nesse caso usa o padrao do codigo)."""
    linhas = (
        session.query(NivelPermissao.PERMISSAO)
        .filter(NivelPermissao.NIVEL == nivel)
        .all()
    )
    if not linhas:
        return None
    return {linha[0] for linha in linhas}


def permissoes_do_nivel(nivel, session=None):
    """Permissoes de um nivel: personalizadas (se existirem no banco) ou o
    padrao do codigo. 'session' e opcional de proposito — sem ela (como nos
    testes unitarios) a funcao nunca toca o banco, so devolve o padrao."""
    if session is not None:
        personalizado = _permissoes_customizadas(session, nivel)
        if personalizado is not None:
            return personalizado

    return set(NIVEIS.get(nivel, {}).get("permissoes", ()))


def substituir_permissoes_nivel(session, nivel, permissoes):
    """Grava o conjunto completo de permissoes desejado para um nivel.

    Levanta ValueError se o nivel nao existe ou se e o Administrador
    (permissoes fixas, ver NIVEIS_PERMISSOES_FIXAS).
    """
    if nivel not in NIVEIS:
        raise ValueError("Nível de acesso inválido.")
    if nivel in NIVEIS_PERMISSOES_FIXAS:
        raise ValueError("As permissões deste nível não podem ser alteradas.")

    validas = {p for p in (permissoes or []) if p in TODAS_PERMISSOES}

    session.query(NivelPermissao).filter(NivelPermissao.NIVEL == nivel).delete()
    for permissao in validas:
        session.add(NivelPermissao(NIVEL=nivel, PERMISSAO=permissao))


def descrever_usuario(usuario, incluir_vinculos=True, session=None):
    """Formato que vai para a tela e para as checagens de permissao."""
    dados = {
        "id": usuario.id,
        "usuario": usuario.USUARIO,
        "nome": usuario.NOME,
        "nivel": usuario.NIVEL,
        "nivel_rotulo": NIVEIS.get(usuario.NIVEL, {}).get("rotulo", usuario.NIVEL),
        "ativo": bool(usuario.ATIVO),
        "permissoes": sorted(permissoes_do_nivel(usuario.NIVEL, session)),
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


def pode_atuar_na_base_e_tipo(usuario, base, tipo_equipe):
    """Diz se o usuario pode alocar/remover numa vaga daquela base e tipo.

    ADMINISTRADOR (ignora_vinculos) sempre pode. Os demais precisam ter um vinculo
    BASE que bata com a base da vaga E um vinculo TIPO_EQUIPE que bata com o
    tipo dela — as duas coisas ao mesmo tempo, nao uma ou outra.
    """
    if not usuario:
        return False
    if usuario.get("ignora_vinculos"):
        return True

    vinculos = usuario.get("vinculos") or {}
    bases = set(vinculos.get(VINCULO_BASE, []))
    tipos = set(vinculos.get(VINCULO_TIPO_EQUIPE, []))

    return base in bases and tipo_equipe in tipos


def pode_realizar_operacao(
    usuario, operacao, base, tipo_equipe, equipe_id=None, setor=None
):
    """Diz se o usuario pode ALOCAR/EDITAR/REMOVER numa vaga/equipe dada.

    "O que pode fazer" e a PERMISSAO do nivel (ver PERMISSAO_POR_OPERACAO —
    editavel na tela de Usuarios > Niveis de acesso, igual as demais
    permissoes). "Sobre quais equipes" continua nos vinculos do usuario.

    ADMINISTRADOR (ignora_vinculos) sempre pode.
    SUPERVISOR e ANALISTA: precisam ter a permissao da operacao E bater em
      pelo menos um recorte de dados: equipe especifica (vinculo EQUIPE),
      ou base+tipo juntos, ou setor (vinculo SETOR).
    """
    if not usuario:
        return False
    if usuario.get("ignora_vinculos"):
        return True

    permissao_necessaria = PERMISSAO_POR_OPERACAO.get(operacao)
    if permissao_necessaria and permissao_necessaria not in (usuario.get("permissoes") or ()):
        return False

    nivel = usuario.get("nivel")
    vinculos = usuario.get("vinculos") or {}

    if nivel == NIVEL_ANALISTA:
        equipes = set(vinculos.get(VINCULO_EQUIPE, []))
        if equipe_id is not None and str(equipe_id) in equipes:
            return True

        setores = set(vinculos.get(VINCULO_SETOR, []))
        if setor and setor in setores:
            return True

        return pode_atuar_na_base_e_tipo(usuario, base, tipo_equipe)

    if nivel == NIVEL_SUPERVISOR:
        return pode_atuar_na_base_e_tipo(usuario, base, tipo_equipe)

    # Nivel sem regra de escopo definida: nega por padrao.
    return False


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
