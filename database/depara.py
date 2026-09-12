# -*- coding: utf-8 -*-
"""De-para de SEÇÃO e RATEIO_FUNCIONARIO, importados uma única vez da
planilha que o Igor mandou (ver database/importacao/depara_cadastro.json
para a origem exata e a data da importação).

Por que isso vira um arquivo no repositório, e não uma leitura do Excel em
tempo de execução: o Excel original só ficou disponível uma vez para
consulta. O JSON versionado é a fonte de verdade dali em diante — se um
código ou seção novos aparecerem no cadastro sem estar aqui, a tradução
cai no fallback (usa o texto cru) em vez de quebrar, mas o valor tratado
não vem automaticamente: é preciso atualizar o JSON manualmente.

Dois de-paras, sem relação um com o outro (o arquivo original não tinha
nenhuma coluna ligando as duas abas):

- SEÇÃO: texto cru de Colaborador.SEÇÃO -> nome de base tratado (BACABAL,
  PRES DUTRA, ITAPECURU...). Substitui o DE_PARA_SECOES que existia direto
  em app.py — a mesma tradução agora serve tanto para agrupar "não
  alocados" por base quanto para a nova coluna "Seção tratada" da tela de
  Colaboradores.
- RATEIO_FUNCIONARIO: código do rateio (Rateio.RATEIO_FUNCIONARIO, ex:
  "2.127.05") -> "tipo de ccusto" tratado (CONSTRUÇÃO, PODA, TRANSPORTE,
  ADMINISTRATIVO...). Não tem nenhuma relação com o "tipo de equipe"
  operacional (LIGAÇÃO NOVA, CONSTRUÇÃO como ESTRUTURA de vaga) — são coisas
  diferentes que coincidem de usar as mesmas palavras.
"""
import json
import unicodedata
from pathlib import Path

_ARQUIVO_JSON = Path(__file__).parent / "importacao" / "depara_cadastro.json"


def _normalizar(texto):
    """Caixa alta e sem acento — mesma regra usada em app.py:normalizar(),
    duplicada aqui (sem import) para este módulo não depender de app.py."""
    if texto is None:
        return ""
    texto = str(texto).strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _carregar():
    with open(_ARQUIVO_JSON, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    secao = {_normalizar(bruto): tratado for bruto, tratado in dados["secao"].items()}
    rateio = {codigo.strip(): tratado for codigo, tratado in dados["rateio"].items()}
    return secao, rateio, dados.get("_origem", ""), dados.get("_importado_em", "")


DE_PARA_SECAO, DE_PARA_TIPO_CCUSTO, ORIGEM_DEPARA, IMPORTADO_EM_DEPARA = _carregar()


def secao_tratada(secao_bruta):
    """Nome de base tratado para o texto cru de Colaborador.SEÇÃO. Sem
    tradução cadastrada, devolve o próprio texto (limpo), igual ao
    comportamento antigo de base_da_secao em app.py."""
    if not secao_bruta:
        return ""
    return DE_PARA_SECAO.get(_normalizar(secao_bruta), str(secao_bruta).strip())


def tipo_ccusto_do_codigo(codigo_rateio):
    """Tipo de ccusto tratado para UM código de rateio. Sem tradução
    cadastrada, devolve o próprio código (mesmo comportamento de
    fallback de secao_tratada)."""
    if not codigo_rateio:
        return ""
    codigo = str(codigo_rateio).strip()
    return DE_PARA_TIPO_CCUSTO.get(codigo, codigo)


def tipos_ccusto_dos_rateios(codigos_rateio):
    """Tipo de ccusto de TODOS os rateios de um colaborador, já tratados e
    sem repetição — na ordem em que apareceram. Uma pessoa com rateio só
    em CONSTRUÇÃO devolve "CONSTRUÇÃO"; rateada entre CONSTRUÇÃO e PODA
    devolve "CONSTRUÇÃO / PODA". Mesmo formato (" / ".join) que a aba de
    consulta da planilha de alocações já usa pra RATEIO/GRPCCUSTO (ver
    montar_planilha_ativos em app.py) — um colaborador rateado não vira
    várias linhas, so os tipos ficam juntos na mesma célula.
    """
    tratados = []
    for codigo in codigos_rateio or []:
        tratado = tipo_ccusto_do_codigo(codigo)
        if tratado and tratado not in tratados:
            tratados.append(tratado)
    return " / ".join(tratados)
