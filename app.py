import unicodedata
from pathlib import Path

from flask import Flask, jsonify, redirect, request, send_from_directory
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
    return str(funcao).strip() if funcao else ""


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

        for equipe in equipes:
            base = str(equipe.BASE).strip() if equipe.BASE is not None else ""
            if not base:
                continue

            codigo_base = DE_PARA_BASES.get(normalizar(base), base)

            if filtro_base:
                filtro_norm = normalizar(filtro_base)
                if filtro_norm not in (normalizar(base), normalizar(codigo_base)):
                    continue

            prefixo = str(equipe.PREFIXO).strip() if equipe.PREFIXO is not None else ""
            tipo_equipe = "FOLGUISTA" if normalizar(prefixo) == "FOLGUISTA" else "CONSTRUÇÃO"

            if base not in resumo_bases:
                resumo_bases[base] = {
                    "base": base,
                    "codigo": codigo_base,
                    "equipes": {"CONSTRUÇÃO": 0, "FOLGUISTA": 0},
                    "funcoes": {"CONSTRUÇÃO": {}, "FOLGUISTA": {}},
                }

            if codigo_base not in pessoas_disponiveis:
                pessoas_disponiveis[codigo_base] = {
                    "base": base,
                    "codigo": codigo_base,
                    "funcoes": {},
                    "detalhes": {},
                }

            resumo_bases[base]["equipes"][tipo_equipe] += 1

            for composicao in (equipe.composicoes or []):
                funcao_exibicao = padronizar_funcao(composicao.FUNÇÃO_ER)
                if not funcao_exibicao:
                    continue

                if funcao_exibicao not in resumo_bases[base]["funcoes"][tipo_equipe]:
                    resumo_bases[base]["funcoes"][tipo_equipe][funcao_exibicao] = {
                        "vagas": 0,
                        "alocados": 0,
                    }

                registro = resumo_bases[base]["funcoes"][tipo_equipe][funcao_exibicao]
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
                            "chapa": str(colaborador.CHAPA).strip(),
                            "nome": str(colaborador.NOME).strip(),
                            "funcao": funcao_colab,
                            "funcao_sistema": str(colaborador.FUNÇÃO).strip() if colaborador.FUNÇÃO else "",
                            "vaga": str(composicao.FUNÇÃO_ER).strip() if composicao.FUNÇÃO_ER else "",
                        })

        resultado = []
        for base, dados_base in resumo_bases.items():
            linhas = []
            for tipo_equipe in ("CONSTRUÇÃO", "FOLGUISTA"):
                funcoes = dados_base["funcoes"][tipo_equipe]
                for funcao, dados_funcao in sorted(funcoes.items(), key=lambda item: ordem_funcao(item[0])):
                    vagas = dados_funcao["vagas"]
                    alocados = dados_funcao["alocados"]
                    linhas.append({
                        "equipe": tipo_equipe,
                        "funcao": funcao,
                        "vagas": vagas,
                        "alocados": alocados,
                        "diferenca": alocados - vagas,
                    })

            resultado.append({
                "base": base,
                "codigo": dados_base["codigo"],
                "equipes": dados_base["equipes"],
                "funcoes": linhas,
            })

        resultado.sort(key=lambda item: item["base"])

        total_construcao = sum(item["equipes"]["CONSTRUÇÃO"] for item in resultado)
        total_folguista = sum(item["equipes"]["FOLGUISTA"] for item in resultado)
        total_vagas = sum(linha["vagas"] for item in resultado for linha in item["funcoes"])
        total_alocados = sum(linha["alocados"] for item in resultado for linha in item["funcoes"])

        total = {
            "base": "TOTAL",
            "equipes": {
                "CONSTRUÇÃO": total_construcao,
                "FOLGUISTA": total_folguista,
            },
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
