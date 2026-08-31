from flask import Flask, render_template, jsonify, request
from sqlalchemy.orm import joinedload

from database.database import SessionLocal
from database.models import (
    Equipe,
    Colaborador,
    ComposicaoEquipe,
    MembroEquipe
)


app = Flask(__name__)


# ============================================================
# DE/PARA DAS BASES
# ============================================================

DE_PARA_BASES = {

    "BACABAL": "BCB",

    "ITAPECURU": "ITM",

    "SANTA INES": "STI",

    "SPOT STI": "SPOT STI",

    "PEDREIRAS": "PDS",

    "PRES DUTRA": "PDT",

    "BARRA DO CORDA": "BDC"

}


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@app.route("/")
def index():

    return render_template(
        "banco_dados.html"
    )


# ============================================================
# PÁGINA DE RESUMO
# ============================================================

@app.route("/resumo")
def resumo():

    return render_template(
        "resumo.html"
    )


# ============================================================
# API DO RESUMO
# ============================================================

@app.route(
    "/api/resumo",
    methods=["GET"]
)
def obter_resumo():

    session = SessionLocal()

    try:

        filtro_base = (
            request.args.get(
                "base",
                ""
            )
            .strip()
        )


        # ====================================================
        # BUSCAR EQUIPES
        # ====================================================

        equipes = (
            session.query(Equipe)
            .options(
                joinedload(
                    Equipe.composicoes
                )
                .joinedload(
                    ComposicaoEquipe.membro
                )
                .joinedload(
                    MembroEquipe.colaborador
                )
            )
            .order_by(
                Equipe.BASE,
                Equipe.PREFIXO
            )
            .all()
        )


        # ====================================================
        # ESTRUTURA
        # ====================================================

        resumo_bases = {}


        # ====================================================
        # PERCORRER EQUIPES
        # ====================================================

        for equipe in equipes:

            base = (
                str(equipe.BASE).strip()
                if equipe.BASE is not None
                else ""
            )


            if not base:
                continue


            codigo_base = DE_PARA_BASES.get(
                normalizar(base),
                base
            )


            # =================================================
            # FILTRO DE BASE
            # =================================================

            if filtro_base:

                filtro_normalizado =normalizar(
                        filtro_base
                    )

                if filtro_normalizado not in (
                    normalizar(base),
                    normalizar(codigo_base)
                ):

                    continue


            prefixo = (
                str(equipe.PREFIXO).strip()
                if equipe.PREFIXO is not None
                else ""
            )


            if (
                normalizar(prefixo)
                == "FOLGUISTA"
            ):

                tipo_equipe = "FOLGUISTA"

            else:

                tipo_equipe = "CONSTRUÇÃO"


            # =================================================
            # CRIAR BASE
            # =================================================

            if base not in resumo_bases:

                resumo_bases[base] = {

                    "base":
                        base,

                    "codigo":
                        codigo_base,

                    "equipes": {

                        "CONSTRUÇÃO": 0,

                        "FOLGUISTA": 0

                    },

                    "funcoes": {

                        "CONSTRUÇÃO": {},

                        "FOLGUISTA": {}

                    }

                }


            resumo_bases[base]["equipes"][
                tipo_equipe
            ] += 1


            # =================================================
            # VAGAS
            # =================================================

            for composicao in (
                equipe.composicoes or []
            ):

                funcao_original = (
                    composicao.FUNÇÃO_ER
                    or ""
                )


                funcao = normalizar(
                    funcao_original
                )


                # ---------------------------------------------
                # PADRONIZAR FUNÇÃO
                # ---------------------------------------------

                if funcao == "ENCARREGADO":

                    funcao_exibicao = (
                        "ENCARREGADO"
                    )

                elif funcao in (
                    "MUNQUEIRO/MOTORISTA",
                    "MOTORISTA"
                ):

                    funcao_exibicao = (
                        "MOTORISTA"
                    )

                elif funcao == "ELETRICISTA":

                    funcao_exibicao = (
                        "ELETRICISTA"
                    )

                elif funcao in (
                    "AUXILIAR DE ELETRICISTA",
                    "AUXILIAR ELETRICISTA"
                ):

                    funcao_exibicao = (
                        "AUXILIAR DE ELETRICISTA"
                    )

                else:

                    funcao_exibicao = (
                        str(
                            funcao_original
                        ).strip()
                    )


                if not funcao_exibicao:

                    continue


                # ---------------------------------------------
                # CRIAR FUNÇÃO
                # ---------------------------------------------

                if (
                    funcao_exibicao
                    not in resumo_bases[base]["funcoes"][
                        tipo_equipe
                    ]
                ):

                    resumo_bases[base]["funcoes"][
                        tipo_equipe
                    ][funcao_exibicao] = {

                        "vagas": 0,

                        "alocados": 0

                    }


                registro = (
                    resumo_bases[base]["funcoes"][
                        tipo_equipe
                    ][funcao_exibicao]
                )


                # ---------------------------------------------
                # VAGA
                # ---------------------------------------------

                registro["vagas"] += 1


                # ---------------------------------------------
                # ALOCADO
                # ---------------------------------------------

                if (
                    composicao.membro
                    and composicao.membro.colaborador
                ):

                    registro["alocados"] += 1


        # ====================================================
        # ORDEM DAS FUNÇÕES
        # ====================================================

        ordem_funcoes = {

            "ENCARREGADO": 1,

            "ELETRICISTA": 2,

            "MOTORISTA": 3,

            "AUXILIAR DE ELETRICISTA": 4

        }


        # ====================================================
        # MONTAR RESULTADO
        # ====================================================

        resultado = []


        for base, dados_base in resumo_bases.items():

            linhas = []


            for tipo_equipe in (
                "CONSTRUÇÃO",
                "FOLGUISTA"
            ):

                funcoes = dados_base["funcoes"][
                        tipo_equipe
                    ]


                for funcao, dados_funcao in sorted(

                    funcoes.items(),

                    key=lambda item:
                        ordem_funcoes.get(
                            item[0],
                            99
                        )

                ):

                    vagas = (
                        dados_funcao["vagas"]
                    )


                    alocados = (
                        dados_funcao["alocados"]
                    )


                    diferenca = (
                        alocados
                        -
                        vagas
                    )


                    linhas.append({

                        "equipe":
                            tipo_equipe,

                        "funcao":
                            funcao,

                        "vagas":
                            vagas,

                        "alocados":
                            alocados,

                        "diferenca":
                            diferenca

                    })


            resultado.append({

                "base":
                    base,

                "codigo":
                    dados_base["codigo"],

                "equipes":
                    dados_base["equipes"],

                "funcoes":
                    linhas

            })


        # ====================================================
        # ORDENAR BASES
        # ====================================================

        resultado.sort(
            key=lambda item:
                item["base"]
        )


        # ====================================================
        # TOTAL GERAL
        # ====================================================

        total_equipes_construcao = sum(

            item["equipes"]["CONSTRUÇÃO"]

            for item in resultado

        )


        total_equipes_folguista = sum(

            item["equipes"]["FOLGUISTA"]

            for item in resultado

        )


        total_vagas = sum(

            linha["vagas"]

            for item in resultado

            for linha in item["funcoes"]

        )


        total_alocados = sum(

            linha["alocados"]

            for item in resultado

            for linha in item["funcoes"]

        )


        total = {

            "base":
                "TOTAL",

            "equipes": {

                "CONSTRUÇÃO":
                    total_equipes_construcao,

                "FOLGUISTA":
                    total_equipes_folguista

            },

            "vagas":
                total_vagas,

            "alocados":
                total_alocados,

            "diferenca":
                total_alocados
                -
                total_vagas

        }


        # ====================================================
        # TOTAL DE PESSOAS DISPONÍVEIS
        #
        # DISPONÍVEL = COLABORADOR ALOCADO EM EQUIPE
        # ====================================================

        pessoas_disponiveis = {}


        for item in resultado:

            base = item["base"]

            codigo = item["codigo"]


            pessoas_disponiveis[codigo] = {

                "base":
                    base,

                "codigo":
                    codigo,

                "funcoes": {}

            }


        # ====================================================
        # CONTAR COLABORADORES ALOCADOS
        # POR FUNÇÃO E BASE
        # ====================================================

        for equipe in equipes:

            base = (
                str(equipe.BASE).strip()
                if equipe.BASE is not None
                else ""
            )


            if not base:
                continue


            codigo_base = DE_PARA_BASES.get(
                normalizar(base),
                base
            )


            if codigo_base not in pessoas_disponiveis:

                continue


            for composicao in (
                equipe.composicoes or []
            ):

                if not (
                    composicao.membro
                    and composicao.membro.colaborador
                ):

                    continue


                colaborador = (
                    composicao.membro.colaborador
                )


                funcao = normalizar(
                    colaborador.FUNÇÃO
                )


                # ---------------------------------------------
                # PADRONIZAR FUNÇÃO DO COLABORADOR
                # ---------------------------------------------

                if funcao == "ENCARREGADO":

                    funcao_exibicao = (
                        "ENCARREGADO"
                    )

                elif funcao in (
                    "ELETRICISTA",
                ):

                    funcao_exibicao = (
                        "ELETRICISTA"
                    )

                elif funcao in (
                    "MOTORISTA",
                    "MUNQUEIRO/MOTORISTA"
                ):

                    funcao_exibicao = (
                        "MOTORISTA"
                    )

                elif funcao in (
                    "AUXILIAR DE ELETRICISTA",
                    "AUXILIAR ELETRICISTA"
                ):

                    funcao_exibicao = (
                        "AUXILIAR DE ELETRICISTA"
                    )

                else:

                    continue


                if (
                    funcao_exibicao
                    not in pessoas_disponiveis[
                        codigo_base
                    ]["funcoes"]
                ):

                    pessoas_disponiveis[
                        codigo_base
                    ]["funcoes"][
                        funcao_exibicao
                    ] = 0


                pessoas_disponiveis[
                    codigo_base
                ]["funcoes"][
                    funcao_exibicao
                ] += 1


        # ====================================================
        # TRANSFORMAR PARA LISTA
        # ====================================================

        lista_disponiveis = []


        for codigo, dados in (
            pessoas_disponiveis.items()
        ):

            lista_disponiveis.append({

                "base":
                    dados["base"],

                "codigo":
                    codigo,

                "funcoes":
                    dados["funcoes"]

            })


        # ====================================================
        # BASES PARA O FILTRO
        # ====================================================

        bases_filtro = []


        for item in resultado:

            bases_filtro.append({

                "base":
                    item["base"],

                "codigo":
                    item["codigo"]

            })


        # ====================================================
        # RETORNO
        # ====================================================

        return jsonify({

            "bases":
                resultado,

            "total":
                total,

            "bases_filtro":
                bases_filtro,

            "base_selecionada":
                filtro_base,

            "pessoas_disponiveis":
                lista_disponiveis

        })


    except Exception as erro:

        print(
            f"[ERRO] obter_resumo: {erro}"
        )


        return jsonify({

            "erro":
                str(erro)

        }), 500


    finally:

        session.close()


# ============================================================
# API - EQUIPES
# ============================================================

@app.route(
    "/api/equipes",
    methods=["GET"]
)
def obter_equipes():

    session = SessionLocal()

    try:

        equipes = (
            session.query(Equipe)
            .options(
                joinedload(
                    Equipe.composicoes
                )
                .joinedload(
                    ComposicaoEquipe.membro
                )
                .joinedload(
                    MembroEquipe.colaborador
                )
            )
            .order_by(
                Equipe.PREFIXO
            )
            .all()
        )


        resultado = []


        for equipe in equipes:

            composicoes = sorted(

                equipe.composicoes,

                key=lambda item: (

                    ordem_funcao(
                        item.FUNÇÃO_ER
                    ),

                    item.id

                )

            )


            vagas = []


            for composicao in composicoes:

                colaborador = None


                if (
                    composicao.membro
                    and composicao.membro.colaborador
                ):

                    colaborador = (
                        composicao.membro.colaborador
                    )


                vagas.append({

                    "id":
                        composicao.id,

                    "funcao_er":
                        (
                            composicao.FUNÇÃO_ER
                            or ""
                        ),

                    "ocupada":
                        (
                            colaborador
                            is not None
                        ),

                    "colaborador": {

                        "chapa":
                            str(
                                colaborador.CHAPA
                            ),

                        "nome":
                            (
                                colaborador.NOME
                                or ""
                            ),

                        "funcao":
                            (
                                colaborador.FUNÇÃO
                                or ""
                            )

                    }

                    if colaborador

                    else None

                })


            resultado.append({

                "id":
                    equipe.id,

                "prefixo":
                    (
                        equipe.PREFIXO
                        or ""
                    ),

                "base":
                    (
                        equipe.BASE
                        or ""
                    ),

                "vagas":
                    vagas

            })


        return jsonify(
            resultado
        )


    except Exception as erro:

        print(
            f"[ERRO] obter_equipes: {erro}"
        )


        return jsonify({

            "erro":
                str(erro)

        }), 500


    finally:

        session.close()


# ============================================================
# API - OPÇÕES DE ALOCAÇÃO
# ============================================================

@app.route(
    "/api/opcoes-alocacao",
    methods=["GET"]
)
def obter_opcoes_alocacao():

    session = SessionLocal()

    try:

        equipes = (
            session.query(Equipe)
            .options(
                joinedload(
                    Equipe.composicoes
                )
                .joinedload(
                    ComposicaoEquipe.membro
                )
            )
            .order_by(
                Equipe.BASE,
                Equipe.PREFIXO
            )
            .all()
        )


        resultado = {}


        for equipe in equipes:

            base = (
                str(equipe.BASE).strip()
                if equipe.BASE is not None
                else ""
            )


            prefixo = (
                str(equipe.PREFIXO).strip()
                if equipe.PREFIXO is not None
                else ""
            )


            if not base:
                continue


            if base not in resultado:

                resultado[base] = []


            vagas = []


            for composicao in (
                equipe.composicoes or []
            ):

                if composicao.membro:

                    continue


                vagas.append({

                    "id":
                        composicao.id,

                    "funcao_er":
                        (
                            composicao.FUNÇÃO_ER
                            or ""
                        ),

                    "estrutura":
                        (
                            composicao.ESTRUTURA
                            or ""
                        )

                })


            resultado[base].append({

                "id":
                    equipe.id,

                "prefixo":
                    prefixo,

                "vagas":
                    vagas

            })


        for base in resultado:

            resultado[base].sort(

                key=lambda equipe: (

                    StringOrdenacaoFolguista(
                        equipe["prefixo"]
                    ),

                    equipe["prefixo"]

                )

            )


        return jsonify(
            resultado
        )


    except Exception as erro:

        print(
            f"[ERRO] obter_opcoes_alocacao: {erro}"
        )


        return jsonify({

            "erro":
                str(erro)

        }), 500


    finally:

        session.close()


# ============================================================
# API - COLABORADORES
# ============================================================

@app.route(
    "/api/colaboradores",
    methods=["GET"]
)
def obter_colaboradores():

    session = SessionLocal()

    try:

        colaboradores = (
            session.query(
                Colaborador
            )
            .order_by(
                Colaborador.NOME
            )
            .all()
        )


        registros_alocados = (
            session.query(
                MembroEquipe.CHAPA
            )
            .filter(
                MembroEquipe.CHAPA.isnot(None)
            )
            .all()
        )


        chapas_alocadas = {

            str(
                registro.CHAPA
            ).strip()

            for registro
            in registros_alocados

        }


        resultado = []


        for colaborador in colaboradores:

            chapa = str(
                colaborador.CHAPA
            ).strip()


            resultado.append({

                "chapa":
                    chapa,

                "nome":
                    (
                        colaborador.NOME
                        or ""
                    ),

                "funcao":
                    (
                        colaborador.FUNÇÃO
                        or ""
                    ),

                "alocado":
                    (
                        chapa
                        in chapas_alocadas
                    )

            })


        return jsonify(
            resultado
        )


    except Exception as erro:

        print(
            f"[ERRO] obter_colaboradores: {erro}"
        )


        return jsonify({

            "erro":
                str(erro)

        }), 500


    finally:

        session.close()


# ============================================================
# ALOCAR COLABORADOR
# ============================================================

@app.route(
    "/api/equipes/alocar",
    methods=["POST"]
)
def alocar_colaborador():

    dados = request.get_json()


    if not dados:

        return jsonify({

            "erro":
                "Dados não enviados."

        }), 400


    composicao_id = dados.get(
        "composicao_id"
    )


    chapa = str(
        dados.get(
            "chapa",
            ""
        )
    ).strip()


    if not composicao_id:

        return jsonify({

            "erro":
                "Vaga não informada."

        }), 400


    if not chapa:

        return jsonify({

            "erro":
                "CHAPA não informada."

        }), 400


    session = SessionLocal()


    try:

        colaborador = (

            session.query(
                Colaborador
            )

            .filter(
                Colaborador.CHAPA == chapa
            )

            .first()

        )


        if not colaborador:

            return jsonify({

                "erro":
                    "Colaborador não encontrado."

            }), 404


        alocacao_existente = (

            session.query(
                MembroEquipe
            )

            .filter(
                MembroEquipe.CHAPA == chapa
            )

            .first()

        )


        if alocacao_existente:

            return jsonify({

                "erro": (
                    "Este colaborador já está "
                    "alocado em outra equipe."
                )

            }), 400


        composicao = (

            session.query(
                ComposicaoEquipe
            )

            .filter(
                ComposicaoEquipe.id
                == composicao_id
            )

            .first()

        )


        if not composicao:

            return jsonify({

                "erro":
                    "Vaga não encontrada."

            }), 404


        if composicao.membro:

            return jsonify({

                "erro":
                    "Esta vaga já está ocupada."

            }), 400


        membro = MembroEquipe(

            composicao_id=
                composicao_id,

            CHAPA=
                chapa

        )


        session.add(
            membro
        )


        session.commit()


        return jsonify({

            "sucesso":
                True,

            "mensagem":
                "Colaborador alocado com sucesso.",

            "colaborador": {

                "chapa":
                    chapa,

                "nome":
                    (
                        colaborador.NOME
                        or ""
                    ),

                "funcao":
                    (
                        colaborador.FUNÇÃO
                        or ""
                    )

            }

        })


    except Exception as erro:

        session.rollback()


        print(
            f"[ERRO] alocar_colaborador: {erro}"
        )


        return jsonify({

            "erro":
                str(erro)

        }), 500


    finally:

        session.close()


# ============================================================
# REMOVER COLABORADOR
# ============================================================

@app.route(
    "/api/equipes/remover",
    methods=["POST"]
)
def remover_colaborador():

    dados = request.get_json()


    if not dados:

        return jsonify({

            "erro":
                "Dados não enviados."

        }), 400


    composicao_id = dados.get(
        "composicao_id"
    )


    if not composicao_id:

        return jsonify({

            "erro":
                "Vaga não informada."

        }), 400


    session = SessionLocal()


    try:

        membro = (

            session.query(
                MembroEquipe
            )

            .filter(
                MembroEquipe.composicao_id
                == composicao_id
            )

            .first()

        )


        if not membro:

            return jsonify({

                "erro": (
                    "Não existe colaborador "
                    "alocado nesta vaga."
                )

            }), 404


        chapa = str(
            membro.CHAPA
        ).strip()


        session.delete(
            membro
        )


        session.commit()


        return jsonify({

            "sucesso":
                True,

            "mensagem":
                "Colaborador removido com sucesso.",

            "chapa":
                chapa

        })


    except Exception as erro:

        session.rollback()


        print(
            f"[ERRO] remover_colaborador: {erro}"
        )


        return jsonify({

            "erro":
                str(erro)

        }), 500


    finally:

        session.close()


# ============================================================
# ORDENAÇÃO DE EQUIPE
# ============================================================

def StringOrdenacaoFolguista(prefixo):

    prefixo = (
        str(prefixo)
        .strip()
        .upper()
    )


    if prefixo == "FOLGUISTA":

        return 1


    return 0


# ============================================================
# NORMALIZAR TEXTO
# ============================================================

def normalizar(texto):

    if texto is None:

        return ""


    import unicodedata


    texto = str(
        texto
    ).strip().upper()


    texto = unicodedata.normalize(
        "NFD",
        texto
    )


    texto = "".join(

        caractere

        for caractere
        in texto

        if unicodedata.category(
            caractere
        ) != "Mn"

    )


    return texto


# ============================================================
# ORDENAR FUNÇÕES
# ============================================================

def ordem_funcao(funcao):

    funcao = normalizar(
        funcao
    )


    if funcao == "ENCARREGADO":

        return 1


    if funcao in (
        "MUNQUEIRO/MOTORISTA",
        "MOTORISTA"
    ):

        return 2


    if funcao == "ELETRICISTA":

        return 3


    if funcao in (
        "AUXILIAR DE ELETRICISTA",
        "AUXILIAR ELETRICISTA"
    ):

        return 4


    return 99


# ============================================================
# STATUS
# ============================================================

@app.route(
    "/api/status"
)
def status():

    return jsonify({

        "status":
            "online",

        "aplicacao":
            "Gerenciador de Equipes"

    })


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    print()

    print(
        "=" * 60
    )

    print(
        "GERENCIADOR DE EQUIPES"
    )

    print(
        "=" * 60
    )

    print(
        "Servidor iniciado."
    )

    print(
        "Base de Dados: http://127.0.0.1:5000/"
    )

    print(
        "Resumo: http://127.0.0.1:5000/resumo"
    )

    print(
        "=" * 60
    )

    print()


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )