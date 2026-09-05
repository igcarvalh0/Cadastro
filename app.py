import io
import unicodedata
from pathlib import Path

import pandas as pd

from flask import (
    Flask,
    jsonify,
    redirect,
    request,
    send_file,
    send_from_directory,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from database.database import SessionLocal
from database.models import (
    Colaborador,
    ComposicaoEquipe,
    Equipe,
    MembroEquipe,
)

app = Flask(__name__, static_folder=None, template_folder=None)

PROJECT_DIR = Path(__file__).resolve().parent
FRONTEND_DIST_DIR = PROJECT_DIR / "frontend" / "dist" / "spa"


def servir_frontend():
    resposta = send_from_directory(FRONTEND_DIST_DIR, "index.html")
    resposta.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return resposta


@app.route("/assets/<path:arquivo>")
def servir_assets_frontend(arquivo):
    resposta = send_from_directory(FRONTEND_DIST_DIR / "assets", arquivo)
    resposta.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return resposta


@app.route("/fonts/<path:arquivo>")
def servir_fontes_frontend(arquivo):
    return send_from_directory(FRONTEND_DIST_DIR / "fonts", arquivo)


@app.route("/icons/<path:arquivo>")
def servir_icones_frontend(arquivo):
    return send_from_directory(FRONTEND_DIST_DIR / "icons", arquivo)


@app.route("/favicon.ico")
def servir_favicon_frontend():
    return send_from_directory(FRONTEND_DIST_DIR, "favicon.ico")


# ============================================================
# DE/PARA DAS BASES E SEÇÕES
# ============================================================

DE_PARA_BASES = {
    "BACABAL": "BCB",
    "ITAPECURU": "ITM",
    "ITAPECURU MIRIM": "ITM",
    "SANTA INES": "STI",
    "SPOT STI": "SPOT STI",
    "PEDREIRAS": "PDS",
    "PRES DUTRA": "PDT",
    "PRESIDENTE DUTRA": "PDT",
    "BARRA DO CORDA": "BDC",
}

DE_PARA_SECOES = {
    "CT 127 - SETOR ADMINISTRATIVO": "BACABAL",
    "CT 127 - SETOR BACABAL": "BACABAL",
    "CT 169 - SETOR BACABAL": "BACABAL",
    "CT 169 - SETOR PRESIDENTE DUTRA": "PRESIDENTE DUTRA",
    "CT 127 - SETOR DE ITAPECURU MIRIM": "ITAPECURU MIRIM",
    "CT 127 - SETOR SANTA INES": "SANTA INES",
    "CT 169 - SETOR DE BARRA DO CORDA": "BARRA DO CORDA",
    "CT 169- SETOR PEDREIRAS": "PEDREIRAS",
    "CT 170 - SETOR SANTA INES": "SANTA INES",
    "CT 170 - SETOR DE BARRA DO CORDA": "BARRA DO CORDA",
    "CT 127 - SETOR DE FROTA": "BACABAL",
    "CT 169 - SETOR SANTA INES": "SANTA INES",
    "CT 169 - SETOR DE ITAPECURU MIRIM": "ITAPECURU MIRIM",
    "BACABAL": "BACABAL",
    "ITAPECURU": "ITAPECURU MIRIM",
    "ITAPECURU MIRIM": "ITAPECURU MIRIM",
    "SANTA INES": "SANTA INES",
    "SPOT STI": "SPOT STI",
    "PEDREIRAS": "PEDREIRAS",
    "PRES DUTRA": "PRESIDENTE DUTRA",
    "PRESIDENTE DUTRA": "PRESIDENTE DUTRA",
    "BARRA DO CORDA": "BARRA DO CORDA",
}

ORDEM_FUNCOES = {
    "ENCARREGADO": 1,
    "ELETRICISTA": 2,
    "MOTORISTA": 3,
    "AUXILIAR DE ELETRICISTA": 4,
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def normalizar(texto):
    if texto is None:
        return ""
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def padronizar_funcao(funcao):
    funcao_norm = normalizar(funcao)
    if funcao_norm == "ENCARREGADO":
        return "ENCARREGADO"
    if funcao_norm == "ELETRICISTA":
        return "ELETRICISTA"
    if funcao_norm in ("MOTORISTA", "MUNQUEIRO/MOTORISTA"):
        return "MOTORISTA"
    if funcao_norm in ("AUXILIAR DE ELETRICISTA", "AUXILIAR ELETRICISTA"):
        return "AUXILIAR DE ELETRICISTA"
    # funcao nova (Podador, etc.): exibe em caixa alta, igual as demais
    return str(funcao).strip().upper() if funcao else ""


def ordem_funcao(funcao):
    funcao_padrao = padronizar_funcao(funcao)
    return ORDEM_FUNCOES.get(funcao_padrao, 99)


def StringOrdenacaoFolguista(prefixo):
    prefixo = str(prefixo).strip().upper()
    return 1 if prefixo == "FOLGUISTA" else 0


def base_da_secao(secao):
    base = DE_PARA_SECOES.get(
        normalizar(secao),
        str(secao).strip() if secao is not None else ""
    )
    return {
        "nome": base,
        "codigo": DE_PARA_BASES.get(normalizar(base), base),
    }


# ============================================================
# ROTAS DE PÁGINAS
# ============================================================

@app.route("/")
def index():
    return servir_frontend()


@app.route("/resumo")
def resumo():
    return redirect("/#/resumo")


# ============================================================
# API - RESUMO
# ============================================================

@app.route("/api/resumo", methods=["GET"])
def obter_resumo():
    session = SessionLocal()
    try:
        filtro_base = request.args.get("base", "").strip()
        filtro_tipo = request.args.get("tipo", "").strip()

        equipes = (
            session.query(Equipe)
            .options(
                joinedload(Equipe.composicoes)
                .joinedload(ComposicaoEquipe.membro)
                .joinedload(MembroEquipe.colaborador)
            )
            .order_by(Equipe.BASE, Equipe.PREFIXO)
            .all()
        )

        resumo_bases = {}
        pessoas_disponiveis = {}
        tipos_existentes = set()

        for equipe in equipes:
            base = str(equipe.BASE).strip() if equipe.BASE is not None else ""
            if not base:
                continue

            codigo_base = DE_PARA_BASES.get(normalizar(base), base)
            prefixo = str(equipe.PREFIXO).strip() if equipe.PREFIXO is not None else ""
            folguista = eh_folguista(prefixo)

            # o tipo alimenta o filtro mesmo quando a base esta filtrada fora
            for composicao in (equipe.composicoes or []):
                tipos_existentes.add(tipo_equipe_da_vaga(composicao))

            if filtro_base:
                filtro_norm = normalizar(filtro_base)
                if filtro_norm not in (normalizar(base), normalizar(codigo_base)):
                    continue

            if base not in resumo_bases:
                resumo_bases[base] = {
                    "base": base,
                    "codigo": codigo_base,
                    "grupos": {},
                }

            if codigo_base not in pessoas_disponiveis:
                pessoas_disponiveis[codigo_base] = {
                    "base": base,
                    "codigo": codigo_base,
                    "funcoes": {},
                    "detalhes": {},
                }

            for composicao in (equipe.composicoes or []):
                tipo = tipo_equipe_da_vaga(composicao)

                if filtro_tipo and normalizar(tipo) != normalizar(filtro_tipo):
                    continue

                funcao_exibicao = padronizar_funcao(composicao.FUNÇÃO_ER)
                if not funcao_exibicao:
                    continue

                chave = "FOLGUISTA" if folguista else tipo
                grupo = resumo_bases[base]["grupos"].setdefault(chave, {
                    "tipo": chave,
                    "folguista": folguista,
                    "prefixos": set(),
                    "funcoes": {},
                })
                grupo["prefixos"].add(prefixo)

                registro = grupo["funcoes"].setdefault(
                    funcao_exibicao, {"vagas": 0, "alocados": 0}
                )
                registro["vagas"] += 1

                if composicao.membro and composicao.membro.colaborador:
                    colaborador = composicao.membro.colaborador
                    registro["alocados"] += 1

                    funcao_colab = padronizar_funcao(colaborador.FUNÇÃO)
                    if funcao_colab in ORDEM_FUNCOES:
                        pessoas_disponiveis[codigo_base]["funcoes"][funcao_colab] = (
                            pessoas_disponiveis[codigo_base]["funcoes"].get(funcao_colab, 0) + 1
                        )
                        pessoas_disponiveis[codigo_base]["detalhes"].setdefault(funcao_colab, []).append({
                            "base": base,
                            "codigo_base": codigo_base,
                            "equipe": prefixo,
                            "tipo": tipo,
                            "chapa": str(colaborador.CHAPA).strip(),
                            "nome": str(colaborador.NOME).strip(),
                            "funcao": funcao_colab,
                            "funcao_sistema": str(colaborador.FUNÇÃO).strip() if colaborador.FUNÇÃO else "",
                            "vaga": str(composicao.FUNÇÃO_ER).strip() if composicao.FUNÇÃO_ER else "",
                        })

        resultado = []
        for base, dados_base in resumo_bases.items():
            grupos = []

            for chave, dados_grupo in sorted(
                dados_base["grupos"].items(),
                key=lambda item: (item[1]["folguista"], item[0]),
            ):
                funcoes = [
                    {
                        "funcao": funcao,
                        "vagas": dados["vagas"],
                        "alocados": dados["alocados"],
                        "diferenca": dados["alocados"] - dados["vagas"],
                    }
                    for funcao, dados in sorted(
                        dados_grupo["funcoes"].items(),
                        key=lambda item: ordem_funcao(item[0]),
                    )
                ]

                vagas = sum(f["vagas"] for f in funcoes)
                alocados = sum(f["alocados"] for f in funcoes)

                grupos.append({
                    "tipo": chave,
                    "folguista": dados_grupo["folguista"],
                    "rotulo": chave,
                    "equipes": len(dados_grupo["prefixos"]),
                    "funcoes": funcoes,
                    "vagas": vagas,
                    "alocados": alocados,
                    "diferenca": alocados - vagas,
                })

            resultado.append({
                "base": base,
                "codigo": dados_base["codigo"],
                "grupos": grupos,
                "equipes": sum(g["equipes"] for g in grupos),
                "vagas": sum(g["vagas"] for g in grupos),
                "alocados": sum(g["alocados"] for g in grupos),
            })

        resultado.sort(key=lambda item: item["base"])

        total_vagas = sum(item["vagas"] for item in resultado)
        total_alocados = sum(item["alocados"] for item in resultado)

        # totais por disciplina, para os chips do topo
        totais_por_grupo = {}
        for item in resultado:
            for grupo in item["grupos"]:
                chave = (grupo["tipo"], grupo["folguista"])
                acumulado = totais_por_grupo.setdefault(chave, {
                    "tipo": grupo["tipo"],
                    "folguista": grupo["folguista"],
                    "rotulo": grupo["rotulo"],
                    "equipes": 0,
                    "vagas": 0,
                    "alocados": 0,
                })
                acumulado["equipes"] += grupo["equipes"]
                acumulado["vagas"] += grupo["vagas"]
                acumulado["alocados"] += grupo["alocados"]

        grupos_totais = [
            {**dados, "diferenca": dados["alocados"] - dados["vagas"]}
            for dados in sorted(
                totais_por_grupo.values(),
                key=lambda d: (d["tipo"], d["folguista"]),
            )
        ]

        total = {
            "base": "TOTAL",
            "grupos": grupos_totais,
            "equipes": sum(g["equipes"] for g in grupos_totais),
            "vagas": total_vagas,
            "alocados": total_alocados,
            "diferenca": total_alocados - total_vagas,
        }

        lista_disponiveis = [
            {
                "base": dados["base"],
                "codigo": codigo,
                "funcoes": dados["funcoes"],
                "detalhes": dados["detalhes"],
            }
            for codigo, dados in pessoas_disponiveis.items()
        ]

        chapas_alocadas = {
            str(r.CHAPA).strip()
            for r in session.query(MembroEquipe.CHAPA).filter(MembroEquipe.CHAPA.isnot(None)).all()
        }

        lista_nao_alocados = []
        for colab in session.query(Colaborador).order_by(Colaborador.NOME).all():
            chapa = str(colab.CHAPA).strip()
            if chapa in chapas_alocadas:
                continue

            secao = str(colab.SEÇÃO).strip() if colab.SEÇÃO else ""
            dados_base = base_da_secao(secao)
            lista_nao_alocados.append({
                "chapa": chapa,
                "nome": str(colab.NOME).strip() if colab.NOME else "",
                "funcao": str(colab.FUNÇÃO).strip() if colab.FUNÇÃO else "",
                "secao": secao,
                "base": dados_base["nome"],
                "codigo": dados_base["codigo"],
            })

        bases_filtro = [{"base": item["base"], "codigo": item["codigo"]} for item in resultado]

        return jsonify({
            "bases": resultado,
            "total": total,
            "bases_filtro": bases_filtro,
            "base_selecionada": filtro_base,
            "tipos_filtro": sorted(tipos_existentes),
            "tipo_selecionado": filtro_tipo,
            "pessoas_disponiveis": lista_disponiveis,
            "pessoas_nao_alocadas": lista_nao_alocados,
        })
    except Exception as erro:
        print(f"[ERRO] obter_resumo: {erro}")
        return jsonify({"erro": "Não foi possível carregar o resumo."}), 500
    finally:
        session.close()


# ============================================================
# API - EQUIPES
# ============================================================

@app.route("/api/equipes", methods=["GET"])
def obter_equipes():
    session = SessionLocal()
    try:
        equipes = (
            session.query(Equipe)
            .options(
                joinedload(Equipe.composicoes)
                .joinedload(ComposicaoEquipe.membro)
                .joinedload(MembroEquipe.colaborador)
            )
            .order_by(Equipe.PREFIXO)
            .all()
        )

        resultado = []
        for equipe in equipes:
            composicoes = sorted(
                equipe.composicoes,
                key=lambda item: (ordem_funcao(item.FUNÇÃO_ER), item.id),
            )

            vagas = []
            for composicao in composicoes:
                colaborador = None
                if composicao.membro and composicao.membro.colaborador:
                    colaborador = composicao.membro.colaborador

                vagas.append({
                    "id": composicao.id,
                    "funcao_er": composicao.FUNÇÃO_ER or "",
                    "tipo": tipo_equipe_da_vaga(composicao),
                    "ocupada": colaborador is not None,
                    "colaborador": {
                        "chapa": str(colaborador.CHAPA),
                        "nome": colaborador.NOME or "",
                        "funcao": colaborador.FUNÇÃO or "",
                    } if colaborador else None,
                })

            resultado.append({
                "id": equipe.id,
                "prefixo": equipe.PREFIXO or "",
                "base": equipe.BASE or "",
                "tipos": tipos_da_equipe(equipe),
                "folguista": eh_folguista(equipe.PREFIXO),
                "vagas": vagas,
            })

        resultado.sort(
            key=lambda equipe: (
                StringOrdenacaoFolguista(equipe["prefixo"]),
                equipe["prefixo"],
            )
        )

        return jsonify(resultado)
    except Exception as erro:
        print(f"[ERRO] obter_equipes: {erro}")
        return jsonify({"erro": "Não foi possível carregar as equipes."}), 500
    finally:
        session.close()


# ============================================================
# API - CADASTRO DE EQUIPES E VAGAS
# ============================================================

@app.route("/api/equipes", methods=["POST"])
def criar_equipe():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados não enviados."}), 400

    base = str(dados.get("base", "")).strip().upper()
    prefixo = str(dados.get("prefixo", "")).strip()

    if not base:
        return jsonify({"erro": "Base não informada."}), 400
    if not prefixo:
        return jsonify({"erro": "Prefixo não informado."}), 400

    session = SessionLocal()
    try:
        existente = (
            session.query(Equipe)
            .filter(Equipe.BASE == base, Equipe.PREFIXO == prefixo)
            .first()
        )
        if existente:
            return jsonify({"erro": "Já existe uma equipe com essa base e prefixo."}), 400

        equipe = Equipe(BASE=base, PREFIXO=prefixo)
        session.add(equipe)
        session.commit()

        return jsonify({
            "sucesso": True,
            "equipe": {"id": equipe.id, "base": equipe.BASE, "prefixo": equipe.PREFIXO},
        })
    except IntegrityError:
        session.rollback()
        return jsonify({"erro": "Já existe uma equipe com essa base e prefixo."}), 400
    except Exception as erro:
        session.rollback()
        print(f"[ERRO] criar_equipe: {erro}")
        return jsonify({"erro": "Não foi possível criar a equipe."}), 500
    finally:
        session.close()


@app.route("/api/equipes/<int:equipe_id>", methods=["PUT"])
def atualizar_equipe(equipe_id):
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados não enviados."}), 400

    base = str(dados.get("base", "")).strip().upper()
    prefixo = str(dados.get("prefixo", "")).strip()

    if not base:
        return jsonify({"erro": "Base não informada."}), 400
    if not prefixo:
        return jsonify({"erro": "Prefixo não informado."}), 400

    session = SessionLocal()
    try:
        equipe = session.query(Equipe).filter(Equipe.id == equipe_id).first()
        if not equipe:
            return jsonify({"erro": "Equipe não encontrada."}), 404

        duplicada = (
            session.query(Equipe)
            .filter(
                Equipe.BASE == base,
                Equipe.PREFIXO == prefixo,
                Equipe.id != equipe_id,
            )
            .first()
        )
        if duplicada:
            return jsonify({"erro": "Já existe uma equipe com essa base e prefixo."}), 400

        equipe.BASE = base
        equipe.PREFIXO = prefixo
        session.commit()

        return jsonify({
            "sucesso": True,
            "equipe": {"id": equipe.id, "base": equipe.BASE, "prefixo": equipe.PREFIXO},
        })
    except IntegrityError:
        session.rollback()
        return jsonify({"erro": "Já existe uma equipe com essa base e prefixo."}), 400
    except Exception as erro:
        session.rollback()
        print(f"[ERRO] atualizar_equipe: {erro}")
        return jsonify({"erro": "Não foi possível atualizar a equipe."}), 500
    finally:
        session.close()


@app.route("/api/equipes/<int:equipe_id>/membros", methods=["DELETE"])
def remover_membros_equipe(equipe_id):
    session = SessionLocal()
    try:
        equipe = session.query(Equipe).filter(Equipe.id == equipe_id).first()
        if not equipe:
            return jsonify({"erro": "Equipe não encontrada."}), 404

        membros = [
            composicao.membro
            for composicao in equipe.composicoes
            if composicao.membro
        ]

        for membro in membros:
            session.delete(membro)

        session.commit()

        return jsonify({
            "sucesso": True,
            "removidos": len(membros),
            "mensagem": f"{len(membros)} colaborador(es) removido(s) da equipe.",
        })
    except Exception as erro:
        session.rollback()
        print(f"[ERRO] remover_membros_equipe: {erro}")
        return jsonify({"erro": "Não foi possível remover os colaboradores da equipe."}), 500
    finally:
        session.close()


@app.route("/api/equipes/<int:equipe_id>", methods=["DELETE"])
def remover_equipe(equipe_id):
    session = SessionLocal()
    try:
        equipe = session.query(Equipe).filter(Equipe.id == equipe_id).first()
        if not equipe:
            return jsonify({"erro": "Equipe não encontrada."}), 404

        if any(composicao.membro for composicao in equipe.composicoes):
            return jsonify({"erro": "Não é possível excluir uma equipe com colaboradores alocados."}), 400

        session.delete(equipe)
        session.commit()

        return jsonify({"sucesso": True, "mensagem": "Equipe removida com sucesso."})
    except Exception as erro:
        session.rollback()
        print(f"[ERRO] remover_equipe: {erro}")
        return jsonify({"erro": "Não foi possível remover a equipe."}), 500
    finally:
        session.close()



# ============================================================
# API - PLANILHA DE EQUIPES (EXPORTAR / IMPORTAR)
# ============================================================

COLUNA_TIPO_EQUIPE = "TIPO EQUIPE"
COLUNAS_FIXAS_PLANILHA = ("BASE", "PREFIXO", COLUNA_TIPO_EQUIPE, "AÇÃO")
COLUNAS_OBRIGATORIAS_PLANILHA = ("BASE", "PREFIXO", "AÇÃO")
ACOES_PLANILHA = ("criar", "editar", "excluir")

TIPO_EQUIPE_PADRAO = "CONSTRUÇÃO"


def eh_folguista(prefixo):
    """Folguista continua sendo indicado pelo prefixo, nao pelo tipo."""
    return normalizar(prefixo) == "FOLGUISTA"


def tipo_equipe_da_vaga(composicao):
    """A disciplina da vaga fica na ESTRUTURA: CONSTRUÇÃO, PODA, LINHA VIVA, TAT...

    Dados antigos gravavam "Folguista" na ESTRUTURA, quando ela ainda separava
    equipe normal de folguista. Nesses casos a disciplina e construcao.
    """
    valor = str(composicao.ESTRUTURA or "").strip()
    if not valor or normalizar(valor) == "FOLGUISTA":
        return TIPO_EQUIPE_PADRAO
    return valor.upper()


def tipos_da_equipe(equipe):
    tipos = {tipo_equipe_da_vaga(c) for c in (equipe.composicoes or [])}
    return sorted(tipos) if tipos else [TIPO_EQUIPE_PADRAO]


def montar_planilha_equipes(session):
    equipes = (
        session.query(Equipe)
        .options(joinedload(Equipe.composicoes))
        .order_by(Equipe.BASE, Equipe.PREFIXO)
        .all()
    )

    funcoes = sorted(
        {
            str(c.FUNÇÃO_ER).strip()
            for e in equipes
            for c in (e.composicoes or [])
            if c.FUNÇÃO_ER
        },
        key=lambda f: (ordem_funcao(f), f),
    )

    linhas = []
    for equipe in equipes:
        # uma linha por disciplina: a equipe Folguista pode ter vagas de
        # construcao e de poda ao mesmo tempo, e cada uma vira uma linha.
        por_tipo = {}
        for composicao in (equipe.composicoes or []):
            tipo = tipo_equipe_da_vaga(composicao)
            funcao = str(composicao.FUNÇÃO_ER).strip()
            por_tipo.setdefault(tipo, {})
            por_tipo[tipo][funcao] = por_tipo[tipo].get(funcao, 0) + 1

        for tipo in sorted(por_tipo):
            linha = {
                "BASE": equipe.BASE,
                "PREFIXO": equipe.PREFIXO,
                COLUNA_TIPO_EQUIPE: tipo,
                "AÇÃO": "editar",
            }
            for funcao in funcoes:
                linha[funcao] = por_tipo[tipo].get(funcao, 0)
            linhas.append(linha)

    return pd.DataFrame(linhas, columns=list(COLUNAS_FIXAS_PLANILHA) + funcoes)


def quantidade_da_celula(valor):
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return 0
    texto = str(valor).strip()
    if not texto or texto.lower() == "nan":
        return 0
    return int(float(texto))


def texto_da_celula(valor):
    texto = str(valor or "").strip()
    return "" if texto.lower() == "nan" else texto


def analisar_planilha_equipes(arquivo, session):
    """Le a planilha e devolve o plano de mudancas, sem gravar nada.

    A unidade de analise e a EQUIPE inteira, nao a linha: todas as linhas de um
    mesmo BASE+PREFIXO descrevem juntas como aquela equipe deve ficar. E o que
    permite trocar o TIPO EQUIPE de uma equipe existente e o sistema entender
    como reclassificacao, em vez de acrescentar uma disciplina nova e deixar as
    vagas antigas orfas.
    """
    try:
        df = pd.read_excel(arquivo)
    except Exception as erro:
        raise ValueError(f"Não foi possível ler a planilha: {erro}")

    colunas = {str(c).strip(): c for c in df.columns}
    faltando = [c for c in COLUNAS_OBRIGATORIAS_PLANILHA if c not in colunas]
    if faltando:
        raise ValueError(f"A planilha precisa das colunas {', '.join(faltando)}.")

    colunas_funcao = [nome for nome in colunas if nome not in COLUNAS_FIXAS_PLANILHA]
    if not colunas_funcao:
        raise ValueError("A planilha precisa de ao menos uma coluna de função.")

    equipes_existentes = {
        (normalizar(e.BASE), normalizar(e.PREFIXO)): e
        for e in session.query(Equipe)
        .options(joinedload(Equipe.composicoes).joinedload(ComposicaoEquipe.membro))
        .all()
    }

    plano = {"criar": [], "editar": [], "excluir": [], "erros": [], "ignoradas": 0}

    def registrar_erro(numero, rotulo, mensagem):
        plano["erros"].append({"linha": numero, "equipe": rotulo, "erro": mensagem})

    # ---------- 1. le as linhas e agrupa por equipe ----------

    equipes_do_arquivo = {}
    vistas = set()

    for indice, linha in df.iterrows():
        numero = int(indice) + 2  # +1 do cabecalho, +1 porque o Excel comeca em 1

        base = texto_da_celula(linha[colunas["BASE"]]).upper()
        prefixo = texto_da_celula(linha[colunas["PREFIXO"]])
        acao = texto_da_celula(linha[colunas["AÇÃO"]]).lower()
        tipo = (
            texto_da_celula(linha[colunas[COLUNA_TIPO_EQUIPE]]).upper()
            if COLUNA_TIPO_EQUIPE in colunas
            else ""
        ) or TIPO_EQUIPE_PADRAO

        if not base and not prefixo and not acao:
            continue

        rotulo = f"{prefixo or '(sem prefixo)'} / {base or '(sem base)'} · {tipo}"

        if not acao:
            plano["ignoradas"] += 1
            continue

        if acao not in ACOES_PLANILHA:
            registrar_erro(numero, rotulo, f"Ação '{acao}' não existe. Use criar, editar ou excluir.")
            continue
        if not base:
            registrar_erro(numero, rotulo, "Base não informada.")
            continue
        if not prefixo:
            registrar_erro(numero, rotulo, "Prefixo não informado.")
            continue

        chave_linha = (normalizar(base), normalizar(prefixo), normalizar(tipo))
        if chave_linha in vistas:
            registrar_erro(numero, rotulo, f"A equipe já aparece na planilha com o tipo {tipo}.")
            continue
        vistas.add(chave_linha)

        try:
            alvos = {
                nome: quantidade_da_celula(linha[colunas[nome]])
                for nome in colunas_funcao
            }
        except (TypeError, ValueError):
            registrar_erro(numero, rotulo, "As quantidades precisam ser números inteiros.")
            continue

        if any(q < 0 for q in alvos.values()):
            registrar_erro(numero, rotulo, "As quantidades não podem ser negativas.")
            continue

        chave_equipe = (normalizar(base), normalizar(prefixo))
        grupo = equipes_do_arquivo.setdefault(chave_equipe, {
            "base": base,
            "prefixo": prefixo,
            "equipe": equipes_existentes.get(chave_equipe),
            "linhas": [],
        })
        grupo["linhas"].append({
            "numero": numero,
            "rotulo": rotulo,
            "tipo": tipo,
            "acao": acao,
            "alvos": {f: q for f, q in alvos.items()},
        })

    # ---------- 2. resolve equipe por equipe ----------

    for dados in equipes_do_arquivo.values():
        equipe = dados["equipe"]
        linhas = dados["linhas"]
        primeira = linhas[0]

        exclusoes = [l for l in linhas if l["acao"] == "excluir"]
        mantidas = [l for l in linhas if l["acao"] != "excluir"]

        # --- exclusoes: apagam as vagas daquela disciplina ---
        for l in exclusoes:
            if not equipe:
                registrar_erro(l["numero"], l["rotulo"], "Equipe não encontrada.")
                continue
            alvo = [
                c for c in equipe.composicoes
                if tipo_equipe_da_vaga(c) == l["tipo"]
            ]
            if not alvo:
                registrar_erro(l["numero"], l["rotulo"], f"A equipe não tem vagas de {l['tipo']}.")
                continue
            ocupadas = sum(1 for c in alvo if c.membro)
            if ocupadas:
                registrar_erro(
                    l["numero"], l["rotulo"],
                    f"Há {ocupadas} colaborador(es) alocado(s) nas vagas de {l['tipo']}. "
                    "Remova antes de excluir."
                )
                continue
            restantes = [
                c for c in equipe.composicoes
                if tipo_equipe_da_vaga(c) != l["tipo"]
            ]
            plano["excluir"].append({
                "linha": l["numero"],
                "equipe": l["rotulo"],
                "equipe_id": equipe.id,
                "tipo": l["tipo"],
                "vagas": len(alvo),
                "apaga_equipe": not restantes and not mantidas,
            })

        if not mantidas:
            continue

        # --- composicao desejada, somando todas as linhas da equipe ---
        desejado = {}
        for l in mantidas:
            for funcao, qtd in l["alvos"].items():
                if qtd:
                    desejado[(l["tipo"], funcao)] = desejado.get((l["tipo"], funcao), 0) + qtd

        # equipe nova: tudo e criacao, sem nada para comparar
        if not equipe:
            if not desejado:
                registrar_erro(primeira["numero"], primeira["rotulo"], "Informe ao menos uma vaga.")
                continue
            for l in mantidas:
                vagas = {f: q for f, q in l["alvos"].items() if q}
                if not vagas:
                    continue
                plano["criar"].append({
                    "linha": l["numero"],
                    "base": dados["base"],
                    "prefixo": dados["prefixo"],
                    "tipo": l["tipo"],
                    "equipe": l["rotulo"],
                    "equipe_id": None,
                    "vagas": vagas,
                    "total": sum(vagas.values()),
                    "era_edicao": l["acao"] == "editar",
                    "equipe_nova": True,
                })
            continue

        # --- composicao atual da equipe, por (disciplina, funcao) ---
        atual = {}
        for composicao in equipe.composicoes:
            chave = (tipo_equipe_da_vaga(composicao), str(composicao.FUNÇÃO_ER).strip())
            atual.setdefault(chave, []).append(composicao)

        # disciplinas que sumiram do arquivo viram alvo 0: e assim que trocar o
        # TIPO EQUIPE de uma equipe reclassifica, em vez de duplicar as vagas.
        tipos_no_arquivo = {l["tipo"] for l in mantidas}
        tipos_excluidos = {l["tipo"] for l in exclusoes}
        for (tipo_atual, funcao) in atual:
            if tipo_atual in tipos_no_arquivo or tipo_atual in tipos_excluidos:
                continue
            desejado.setdefault((tipo_atual, funcao), 0)

        # funcoes que a planilha nao trouxe como coluna ficam de fora do calculo
        funcoes_do_arquivo = set(colunas_funcao)

        faltam = {}     # (tipo, funcao) -> quantidade a acrescentar
        sobram = {}     # (tipo, funcao) -> [composicoes livres a remover]
        problema = None

        for chave in sorted(set(list(desejado.keys()) + list(atual.keys()))):
            tipo_chave, funcao = chave
            if funcao not in funcoes_do_arquivo:
                continue

            alvo = desejado.get(chave, 0)
            existentes = atual.get(chave, [])
            diferenca = alvo - len(existentes)

            if diferenca > 0:
                faltam[chave] = diferenca
            elif diferenca < 0:
                # ocupadas primeiro: retipar uma vaga ocupada e inofensivo (ela
                # mantem id e colaborador, so muda de disciplina), entao elas sao
                # as primeiras candidatas a reclassificacao. O que sobrar depois
                # e o que sera apagado de fato, e ai as livres vem antes.
                sobram[chave] = sorted(
                    existentes,
                    key=lambda c: (c.membro is None, -c.id),
                )[: -diferenca]

        if problema:
            registrar_erro(primeira["numero"], primeira["rotulo"], problema)
            continue

        # --- casa sobra com falta na MESMA funcao: isso e trocar o tipo da vaga ---
        mudancas = []
        for (tipo_falta, funcao), quantidade in list(faltam.items()):
            for (tipo_sobra, funcao_sobra), livres in list(sobram.items()):
                if funcao_sobra != funcao or not livres or not quantidade:
                    continue
                movidas = min(quantidade, len(livres))
                ids = [c.id for c in livres[:movidas]]
                mudancas.append({
                    "funcao": funcao,
                    "retipar": movidas,
                    "de": tipo_sobra,
                    "para": tipo_falta,
                    "ids": ids,
                })
                del livres[:movidas]
                quantidade -= movidas
                if not livres:
                    del sobram[(tipo_sobra, funcao_sobra)]
            if quantidade:
                faltam[(tipo_falta, funcao)] = quantidade
            else:
                del faltam[(tipo_falta, funcao)]

        for (tipo_chave, funcao), quantidade in faltam.items():
            mudancas.append({"funcao": funcao, "adicionar": quantidade, "tipo": tipo_chave})

        ocupadas_a_apagar = [
            (tipo_chave, funcao, c)
            for (tipo_chave, funcao), restantes in sobram.items()
            for c in restantes
            if c.membro
        ]
        if ocupadas_a_apagar:
            tipo_chave, funcao, _ = ocupadas_a_apagar[0]
            registrar_erro(
                primeira["numero"], primeira["rotulo"],
                f"Sobra {len(ocupadas_a_apagar)} vaga(s) ocupada(s) de {funcao} "
                f"em {tipo_chave} para apagar. Remova os colaboradores antes."
            )
            continue

        for (tipo_chave, funcao), restantes in sobram.items():
            if restantes:
                mudancas.append({
                    "funcao": funcao,
                    "remover": len(restantes),
                    "tipo": tipo_chave,
                    "ids": [c.id for c in restantes],
                })

        if not mudancas:
            plano["ignoradas"] += len(mantidas)
            continue

        def descrever(m):
            if "retipar" in m:
                return f"{m['retipar']} {m['funcao']}: {m['de']} → {m['para']}"
            if "adicionar" in m:
                return f"+{m['adicionar']} {m['funcao']} ({m['tipo']})"
            return f"-{m['remover']} {m['funcao']} ({m['tipo']})"

        plano["editar"].append({
            "linha": primeira["numero"],
            "equipe": f"{dados['prefixo']} / {dados['base']}",
            "equipe_id": equipe.id,
            "mudancas": mudancas,
            "resumo": ", ".join(descrever(m) for m in mudancas),
        })

    return plano


@app.route("/api/equipes/planilha", methods=["GET"])
def baixar_planilha_equipes():
    session = SessionLocal()
    try:
        df = montar_planilha_equipes(session)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Equipes")
            planilha = writer.sheets["Equipes"]
            for coluna in planilha.columns:
                largura = max(
                    len(str(celula.value)) if celula.value is not None else 0
                    for celula in coluna
                )
                planilha.column_dimensions[coluna[0].column_letter].width = max(
                    12, largura + 3
                )
            planilha.freeze_panes = "A2"

        buffer.seek(0)
        return send_file(
            buffer,
            mimetype=(
                "application/vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            ),
            as_attachment=True,
            download_name="equipes.xlsx",
        )
    except Exception as erro:
        print(f"[ERRO] baixar_planilha_equipes: {erro}")
        return jsonify({"erro": "Não foi possível gerar a planilha."}), 500
    finally:
        session.close()


@app.route("/api/equipes/planilha/previa", methods=["POST"])
def prever_planilha_equipes():
    arquivo = request.files.get("arquivo")
    if not arquivo:
        return jsonify({"erro": "Arquivo não enviado."}), 400

    session = SessionLocal()
    try:
        return jsonify(analisar_planilha_equipes(arquivo, session))
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400
    except Exception as erro:
        print(f"[ERRO] prever_planilha_equipes: {erro}")
        return jsonify({"erro": "Não foi possível analisar a planilha."}), 500
    finally:
        session.close()


@app.route("/api/equipes/planilha/aplicar", methods=["POST"])
def aplicar_planilha_equipes():
    arquivo = request.files.get("arquivo")
    if not arquivo:
        return jsonify({"erro": "Arquivo não enviado."}), 400

    session = SessionLocal()
    try:
        plano = analisar_planilha_equipes(arquivo, session)

        if plano["erros"]:
            return jsonify({
                "erro": "A planilha tem linhas com problema. Corrija antes de aplicar.",
                "plano": plano,
            }), 400

        criadas = set()

        for item in plano["criar"]:
            equipe_id = item["equipe_id"]
            if equipe_id is None:
                equipe = Equipe(BASE=item["base"], PREFIXO=item["prefixo"])
                session.add(equipe)
                session.flush()
                equipe_id = equipe.id
                criadas.add(equipe_id)
                # outras linhas da mesma equipe (outra disciplina) reaproveitam o id
                for outro in plano["criar"]:
                    if (
                        outro["equipe_id"] is None
                        and normalizar(outro["base"]) == normalizar(item["base"])
                        and normalizar(outro["prefixo"]) == normalizar(item["prefixo"])
                    ):
                        outro["equipe_id"] = equipe_id

            for funcao, quantidade in item["vagas"].items():
                for _ in range(quantidade):
                    session.add(ComposicaoEquipe(
                        equipe_id=equipe_id,
                        FUNÇÃO_ER=funcao,
                        ESTRUTURA=item["tipo"],
                    ))

        for item in plano["editar"]:
            for mudanca in item["mudancas"]:
                if "adicionar" in mudanca:
                    for _ in range(mudanca["adicionar"]):
                        session.add(ComposicaoEquipe(
                            equipe_id=item["equipe_id"],
                            FUNÇÃO_ER=mudanca["funcao"],
                            ESTRUTURA=mudanca["tipo"],
                        ))
                    continue

                for composicao_id in mudanca["ids"]:
                    composicao = (
                        session.query(ComposicaoEquipe)
                        .filter(ComposicaoEquipe.id == composicao_id)
                        .first()
                    )
                    if not composicao:
                        continue

                    if "retipar" in mudanca:
                        # troca so a disciplina da vaga: id e colaborador ficam,
                        # entao retipar uma vaga ocupada e seguro
                        composicao.ESTRUTURA = mudanca["para"]
                    elif not composicao.membro:
                        session.delete(composicao)

        for item in plano["excluir"]:
            equipe = (
                session.query(Equipe)
                .filter(Equipe.id == item["equipe_id"])
                .first()
            )
            if not equipe:
                continue

            for composicao in list(equipe.composicoes):
                if tipo_equipe_da_vaga(composicao) == item["tipo"] and not composicao.membro:
                    session.delete(composicao)

            if item["apaga_equipe"]:
                session.delete(equipe)

        session.commit()

        return jsonify({
            "sucesso": True,
            "criadas": len(plano["criar"]),
            "editadas": len(plano["editar"]),
            "excluidas": len(plano["excluir"]),
            "ignoradas": plano["ignoradas"],
        })
    except ValueError as erro:
        session.rollback()
        return jsonify({"erro": str(erro)}), 400
    except Exception as erro:
        session.rollback()
        print(f"[ERRO] aplicar_planilha_equipes: {erro}")
        return jsonify({"erro": "Não foi possível aplicar a planilha."}), 500
    finally:
        session.close()


@app.route("/api/equipes/vagas", methods=["POST"])
def criar_vaga():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados não enviados."}), 400

    equipe_id = dados.get("equipe_id")
    funcao_er = str(dados.get("funcao_er", "")).strip()
    estrutura = str(dados.get("estrutura", "")).strip()

    if not equipe_id:
        return jsonify({"erro": "Equipe não informada."}), 400
    if not funcao_er:
        return jsonify({"erro": "Função da vaga não informada."}), 400
    if not estrutura:
        return jsonify({"erro": "Estrutura não informada."}), 400

    session = SessionLocal()
    try:
        equipe = session.query(Equipe).filter(Equipe.id == equipe_id).first()
        if not equipe:
            return jsonify({"erro": "Equipe não encontrada."}), 404

        vaga = ComposicaoEquipe(equipe_id=equipe_id, FUNÇÃO_ER=funcao_er, ESTRUTURA=estrutura)
        session.add(vaga)
        session.commit()

        return jsonify({
            "sucesso": True,
            "vaga": {"id": vaga.id, "funcao_er": vaga.FUNÇÃO_ER, "estrutura": vaga.ESTRUTURA},
        })
    except Exception as erro:
        session.rollback()
        print(f"[ERRO] criar_vaga: {erro}")
        return jsonify({"erro": "Não foi possível criar a vaga."}), 500
    finally:
        session.close()


@app.route("/api/equipes/vagas/<int:vaga_id>", methods=["DELETE"])
def remover_vaga(vaga_id):
    session = SessionLocal()
    try:
        vaga = session.query(ComposicaoEquipe).filter(ComposicaoEquipe.id == vaga_id).first()
        if not vaga:
            return jsonify({"erro": "Vaga não encontrada."}), 404

        if vaga.membro:
            return jsonify({"erro": "Não é possível excluir uma vaga ocupada. Remova o colaborador antes."}), 400

        session.delete(vaga)
        session.commit()

        return jsonify({"sucesso": True, "mensagem": "Vaga removida com sucesso."})
    except Exception as erro:
        session.rollback()
        print(f"[ERRO] remover_vaga: {erro}")
        return jsonify({"erro": "Não foi possível remover a vaga."}), 500
    finally:
        session.close()


# ============================================================
# API - OPÇÕES DE ALOCAÇÃO
# ============================================================

@app.route("/api/opcoes-alocacao", methods=["GET"])
def obter_opcoes_alocacao():
    session = SessionLocal()
    try:
        equipes = (
            session.query(Equipe)
            .options(
                joinedload(Equipe.composicoes)
                .joinedload(ComposicaoEquipe.membro)
            )
            .order_by(Equipe.BASE, Equipe.PREFIXO)
            .all()
        )

        resultado = {}
        for equipe in equipes:
            base = str(equipe.BASE).strip() if equipe.BASE is not None else ""
            prefixo = str(equipe.PREFIXO).strip() if equipe.PREFIXO is not None else ""

            if not base:
                continue

            if base not in resultado:
                resultado[base] = []

            vagas = [
                {
                    "id": composicao.id,
                    "funcao_er": composicao.FUNÇÃO_ER or "",
                    "estrutura": composicao.ESTRUTURA or "",
                }
                for composicao in (equipe.composicoes or [])
                if not composicao.membro
            ]

            resultado[base].append({
                "id": equipe.id,
                "prefixo": prefixo,
                "vagas": vagas,
            })

        for base in resultado:
            resultado[base].sort(
                key=lambda eq: (
                    StringOrdenacaoFolguista(eq["prefixo"]),
                    eq["prefixo"],
                )
            )

        return jsonify(resultado)
    except Exception as erro:
        print(f"[ERRO] obter_opcoes_alocacao: {erro}")
        return jsonify({"erro": "Não foi possível carregar as opções de alocação."}), 500
    finally:
        session.close()


# ============================================================
# API - COLABORADORES
# ============================================================

@app.route("/api/colaboradores", methods=["GET"])
def obter_colaboradores():
    session = SessionLocal()
    try:
        colaboradores = session.query(Colaborador).order_by(Colaborador.NOME).all()
        registros_alocados = (
            session.query(MembroEquipe.CHAPA)
            .filter(MembroEquipe.CHAPA.isnot(None))
            .all()
        )
        chapas_alocadas = {str(r.CHAPA).strip() for r in registros_alocados}

        resultado = []
        for colaborador in colaboradores:
            chapa = str(colaborador.CHAPA).strip()
            dados_base = base_da_secao(colaborador.SEÇÃO)

            resultado.append({
                "chapa": chapa,
                "nome": colaborador.NOME or "",
                "funcao": colaborador.FUNÇÃO or "",
                "secao": colaborador.SEÇÃO or "",
                "base": dados_base["nome"],
                "codigo_base": dados_base["codigo"],
                "alocado": chapa in chapas_alocadas,
            })

        return jsonify(resultado)
    except Exception as erro:
        print(f"[ERRO] obter_colaboradores: {erro}")
        return jsonify({"erro": "Não foi possível carregar os colaboradores."}), 500
    finally:
        session.close()


# ============================================================
# ALOCAR COLABORADOR
# ============================================================

@app.route("/api/equipes/alocar", methods=["POST"])
def alocar_colaborador():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados não enviados."}), 400

    composicao_id = dados.get("composicao_id")
    chapa = str(dados.get("chapa", "")).strip()

    if not composicao_id:
        return jsonify({"erro": "Vaga não informada."}), 400
    if not chapa:
        return jsonify({"erro": "CHAPA não informada."}), 400

    session = SessionLocal()
    try:
        with session.begin():
            colaborador = (
                session.query(Colaborador)
                .filter(Colaborador.CHAPA == chapa)
                .first()
            )
            if not colaborador:
                return jsonify({"erro": "Colaborador não encontrado."}), 404

            alocacao_existente = (
                session.query(MembroEquipe)
                .filter(MembroEquipe.CHAPA == chapa)
                .first()
            )
            if alocacao_existente:
                return jsonify({"erro": "Este colaborador já está alocado em outra equipe."}), 400

            composicao = (
                session.query(ComposicaoEquipe)
                .filter(ComposicaoEquipe.id == composicao_id)
                .with_for_update()
                .first()
            )
            if not composicao:
                return jsonify({"erro": "Vaga não encontrada."}), 404

            if composicao.membro:
                return jsonify({"erro": "Esta vaga já está ocupada."}), 400

            membro = MembroEquipe(composicao_id=composicao_id, CHAPA=chapa)
            session.add(membro)

        return jsonify({
            "sucesso": True,
            "mensagem": "Colaborador alocado com sucesso.",
            "colaborador": {
                "chapa": chapa,
                "nome": colaborador.NOME or "",
                "funcao": colaborador.FUNÇÃO or "",
            },
        })
    except IntegrityError:
        session.rollback()
        return jsonify({"erro": "Este colaborador já está alocado em outra equipe, ou a vaga já está ocupada."}), 400
    except Exception as erro:
        session.rollback()
        print(f"[ERRO] alocar_colaborador: {erro}")
        return jsonify({"erro": "Não foi possível alocar o colaborador."}), 500
    finally:
        session.close()


# ============================================================
# REMOVER COLABORADOR
# ============================================================

@app.route("/api/equipes/remover", methods=["POST"])
def remover_colaborador():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados não enviados."}), 400

    composicao_id = dados.get("composicao_id")
    if not composicao_id:
        return jsonify({"erro": "Vaga não informada."}), 400

    session = SessionLocal()
    try:
        membro = (
            session.query(MembroEquipe)
            .filter(MembroEquipe.composicao_id == composicao_id)
            .first()
        )
        if not membro:
            return jsonify({"erro": "Não existe colaborador alocado nesta vaga."}), 404

        chapa = str(membro.CHAPA).strip()
        session.delete(membro)
        session.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Colaborador removido com sucesso.",
            "chapa": chapa,
        })
    except Exception as erro:
        session.rollback()
        print(f"[ERRO] remover_colaborador: {erro}")
        return jsonify({"erro": "Não foi possível remover o colaborador."}), 500
    finally:
        session.close()


# ============================================================
# STATUS
# ============================================================

@app.route("/api/status")
def status():
    return jsonify({
        "status": "online",
        "aplicacao": "Gerenciador de Equipes",
    })


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    from waitress import serve

    print()
    print("=" * 60)
    print("GERENCIADOR DE EQUIPES")
    print("=" * 60)
    print("Servidor iniciado.")
    print("Base de Dados: http://127.0.0.1:5000/")
    print("Resumo: http://127.0.0.1:5000/resumo")
    print("=" * 60)
    print()

    serve(app, host="127.0.0.1", port=5000)
