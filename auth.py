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
from sqlalchemy.orm import joinedload
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
NIVEL_GERENTE = "GERENTE"
NIVEL_COORDENADOR = "COORDENADOR"
NIVEL_SUPERVISOR = "SUPERVISOR"

# Niveis que ficam acima do Supervisor na hierarquia e herdam escopo dos
# Supervisores abaixo deles (ver escopo_efetivo). Nao tem vinculo proprio.
NIVEIS_HIERARQUICOS = (NIVEL_GERENTE, NIVEL_COORDENADOR)

# Nivel que cada um destes pode escolher como RESPONSAVEL_ID (o superior
# direto): um Coordenador responde a um Gerente, um Supervisor a um
# Coordenador. Gerente nao tem responsavel (topo da arvore).
NIVEL_DO_RESPONSAVEL = {
    NIVEL_COORDENADOR: NIVEL_GERENTE,
    NIVEL_SUPERVISOR: NIVEL_COORDENADOR,
}

# ------------------------------------------------------------
# NIVEIS
# ------------------------------------------------------------
# Os demais niveis entram aqui quando as regras forem definidas: basta uma
# linha nova com o nome e a lista de permissoes. A tela de usuarios le esta
# tabela, entao um nivel novo aparece no formulario sem precisar mexer no
# frontend.
#
# O nivel antigo "MESTRE" foi renomeado para "ADMINISTRADOR" (codigo e banco
# — ver migrations/006_renomear_mestre_para_administrador.sql). O nivel
# "ANALISTA" foi descontinuado (nenhum usuario real o usava) em favor da
# hierarquia Gerente -> Coordenador -> Supervisor (migrations/008).
NIVEIS = {
    NIVEL_ADMINISTRADOR: {
        "rotulo": "Administrador",
        "descricao": "Acesso total, inclusive ao cadastro de usuários.",
        "permissoes": set(TODAS_PERMISSOES),
        "ignora_vinculos": True,
    },
    NIVEL_GERENTE: {
        "rotulo": "Gerente",
        "descricao": (
            "Aloca e remove colaboradores em todas as equipes e bases dos "
            "Coordenadores sob sua responsabilidade (e dos Supervisores "
            "deles)."
        ),
        "permissoes": {VER_RESUMO, VER_EQUIPES, ALOCAR, REMOVER_ALOCACAO},
        "ignora_vinculos": False,
    },
    NIVEL_COORDENADOR: {
        "rotulo": "Coordenador",
        "descricao": (
            "Aloca e remove colaboradores em todas as equipes e bases dos "
            "Supervisores sob sua responsabilidade."
        ),
        "permissoes": {VER_RESUMO, VER_EQUIPES, ALOCAR, REMOVER_ALOCACAO},
        "ignora_vinculos": False,
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
VINCULO_EQUIPE = "EQUIPE"          # id de uma equipe especifica

# SUPERVISOR e COORDENADOR existiram aqui como vinculo (texto livre) antes da
# hierarquia Gerente -> Coordenador -> Supervisor existir. Esse laco agora e
# RESPONSAVEL_ID (o campo "Responde a" na tela, ver escopo_efetivo) — manter
# os dois de pe causava confusao (um Supervisor ligado ao Coordenador pelo
# vinculo errado, e nao pelo responsavel, ficava fora do escopo dele). Nao
# recriar um vinculo chamado "Coordenador"/"Supervisor": quem manda nisso e
# RESPONSAVEL_ID.
#
# BASE e TIPO_EQUIPE sao obrigatorios para enxergar/agir numa vaga (ver
# pode_atuar_na_base_e_tipo). SETOR e EQUIPE sao filtros OPCIONAIS que so
# entram em vigor quando o usuario tem aquele vinculo cadastrado — sem ele, a
# dimensao correspondente nao restringe nada, pra nao quebrar quem so usa
# BASE+TIPO_EQUIPE. O valor de SETOR casa com o campo SETOR da vaga (editavel
# na tela de vagas e na planilha de equipes, ver ComposicaoEquipe.SETOR).
TIPOS_VINCULO = {
    VINCULO_BASE: "Base",
    VINCULO_TIPO_EQUIPE: "Tipo de equipe",
    VINCULO_SETOR: "Setor",
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


def _supervisores_subordinados(session, usuario_id, visitados=None):
    """Todos os usuarios NIVEL_SUPERVISOR alcancaveis a partir de usuario_id
    descendo a arvore de RESPONSAVEL_ID (Gerente -> Coordenador -> Supervisor).

    'visitados' evita loop infinito se alguem cadastrar um ciclo por engano
    (ex.: A responde a B e B responde a A).
    """
    visitados = visitados if visitados is not None else set()
    if usuario_id in visitados:
        return []
    visitados.add(usuario_id)

    filhos = (
        session.query(Usuario)
        .options(joinedload(Usuario.vinculos))
        .filter(Usuario.RESPONSAVEL_ID == usuario_id)
        .all()
    )

    supervisores = []
    for filho in filhos:
        if filho.NIVEL == NIVEL_SUPERVISOR:
            supervisores.append(filho)
        else:
            supervisores.extend(_supervisores_subordinados(session, filho.id, visitados))
    return supervisores


def escopo_efetivo(session, usuario):
    """Para GERENTE/COORDENADOR: uniao dos vinculos de todos os Supervisores
    abaixo dele na hierarquia (RESPONSAVEL_ID). E o que faz 'alocar nas
    equipes dos Supervisores sob sua responsabilidade' virar uma checagem de
    dados de verdade, e nao so uma frase na tela.

    SETOR e EQUIPE so entram no resultado quando algum Supervisor os usa —
    ausencia continua significando 'nao restringe' (ver pode_atuar_na_base_e_tipo).
    """
    bases = set()
    tipos = set()
    setores = set()
    equipes = set()

    for supervisor in _supervisores_subordinados(session, usuario.id):
        for vinculo in supervisor.vinculos:
            if vinculo.TIPO == VINCULO_BASE:
                bases.add(vinculo.VALOR)
            elif vinculo.TIPO == VINCULO_TIPO_EQUIPE:
                tipos.add(vinculo.VALOR)
            elif vinculo.TIPO == VINCULO_SETOR:
                setores.add(vinculo.VALOR)
            elif vinculo.TIPO == VINCULO_EQUIPE:
                equipes.add(vinculo.VALOR)

    escopo = {VINCULO_BASE: sorted(bases), VINCULO_TIPO_EQUIPE: sorted(tipos)}
    if setores:
        escopo[VINCULO_SETOR] = sorted(setores)
    if equipes:
        escopo[VINCULO_EQUIPE] = sorted(equipes)
    return escopo


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
        "responsavel_id": usuario.RESPONSAVEL_ID,
        "responsavel_nome": usuario.responsavel.NOME if usuario.responsavel else None,
    }

    if incluir_vinculos:
        if usuario.NIVEL in NIVEIS_HIERARQUICOS and session is not None:
            # Gerente/Coordenador nao tem vinculo proprio: o escopo dele E a
            # soma dos vinculos dos Supervisores abaixo, calculada agora.
            dados["vinculos"] = escopo_efetivo(session, usuario)
        else:
            vinculos = {}
            for vinculo in usuario.vinculos:
                vinculos.setdefault(vinculo.TIPO, []).append(vinculo.VALOR)
            dados["vinculos"] = {tipo: sorted(v) for tipo, v in vinculos.items()}

    return dados


def tem_permissao(permissao, usuario=None):
    usuario = usuario or usuario_logado()
    return bool(usuario) and permissao in usuario["permissoes"]


def pode_atuar_na_base_e_tipo(usuario, base, tipo_equipe, setor=None, equipe_id=None):
    """Diz se o usuario pode alocar/remover numa vaga daquela base e tipo.

    ADMINISTRADOR (ignora_vinculos) sempre pode.

    Para os demais, CADA tipo de vinculo (BASE, TIPO_EQUIPE, SETOR, EQUIPE) e
    um filtro que so entra em jogo quando o usuario TEM aquele vinculo
    cadastrado. Um vinculo ausente nao restringe aquela dimensao: quem tem so
    SETOR=GSTC enxerga todas as equipes de GSTC, em qualquer base e qualquer
    disciplina; quem tem BASE=BACABAL + TIPO_EQUIPE=CONSTRUÇÃO enxerga so a
    construcao de Bacabal. Os filtros presentes valem todos ao mesmo tempo.

    Antes BASE e TIPO_EQUIPE eram obrigatorios, entao um usuario vinculado so
    a um SETOR caia no "base not in bases" (conjunto vazio) e nao via NADA.

    Sem nenhum vinculo o usuario nao ve nada — a regra falha fechada, para uma
    conta sem escopo nunca virar um curinga que enxerga a operacao inteira.
    """
    if not usuario:
        return False
    if usuario.get("ignora_vinculos"):
        return True

    vinculos = usuario.get("vinculos") or {}
    bases = set(vinculos.get(VINCULO_BASE, []))
    tipos = set(vinculos.get(VINCULO_TIPO_EQUIPE, []))
    setores = set(vinculos.get(VINCULO_SETOR, []))
    equipes = set(vinculos.get(VINCULO_EQUIPE, []))

    if not (bases or tipos or setores or equipes):
        return False

    if bases and base not in bases:
        return False

    if tipos and tipo_equipe not in tipos:
        return False

    if setores and setor not in setores:
        return False

    if equipes and (equipe_id is None or str(equipe_id) not in equipes):
        return False

    return True


def equipe_visivel(usuario, base, tipos_e_setores, equipe_id=None):
    """Diz se o usuario pode VER aquela equipe nas telas de Resumo/Banco de
    Dados/Cadastro de Vagas — nao so alocar/remover nela.

    ADMINISTRADOR ve tudo. Os demais (Supervisor, e Coordenador/Gerente pelo
    escopo herdado em usuario['vinculos'], ver escopo_efetivo) so veem a
    equipe se pelo menos uma das vagas dela bater com todos os vinculos do
    usuario — a equipe Folguista, por exemplo, pode ter vagas de varias
    disciplinas e setores ao mesmo tempo, entao basta UMA bater.

    'tipos_e_setores' e uma lista de pares (tipo, setor), um por disciplina
    presente na equipe (SETOR e por vaga — ver tipos_e_setores_da_equipe em
    app.py).
    """
    if not usuario:
        return False
    if usuario.get("ignora_vinculos"):
        return True

    pares = tipos_e_setores or [(None, None)]
    return any(
        pode_atuar_na_base_e_tipo(usuario, base, tipo, setor=setor, equipe_id=equipe_id)
        for tipo, setor in pares
    )


def pode_realizar_operacao(
    usuario, operacao, base, tipo_equipe, equipe_id=None, setor=None
):
    """Diz se o usuario pode ALOCAR/EDITAR/REMOVER numa vaga/equipe dada.

    So depende da PERMISSAO do nivel (ver PERMISSAO_POR_OPERACAO — editavel
    na tela de Usuarios > Niveis de acesso). O vinculo (BASE/TIPO_EQUIPE/
    SETOR/EQUIPE) NAO entra mais nesta checagem — ele continua decidindo o
    que o usuario VE (equipe_visivel, nas telas de Resumo/Banco de
    Dados/Cadastro de Vagas), so nao trava mais a AÇÃO em si.

    Motivo: um Supervisor vinculado a um tipo de equipe (ex.: MULTI) as
    vezes precisa alocar um colaborador que ja esta numa vaga de outra
    disciplina (ex.: CONSTRUÇÃO), invisivel pra ele. A trava antiga barrava
    essa troca legitima com "Seu acesso não cobre a base ou o tipo de
    equipe desta vaga" — em vez disso, quem chama esta funcao (alocar,
    editar-alocacao, remover, planilha de alocacoes) ja mostra de onde o
    colaborador esta saindo (prefixo + tipo de equipe, em "alocacao_atual")
    e pede confirmacao antes de mover.

    base/tipo_equipe/equipe_id/setor ficam no parametro por compatibilidade
    de chamada (nao usados mais aqui).
    """
    if not usuario:
        return False

    permissao_necessaria = PERMISSAO_POR_OPERACAO.get(operacao)
    if permissao_necessaria and permissao_necessaria not in (usuario.get("permissoes") or ()):
        return False

    return True


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
