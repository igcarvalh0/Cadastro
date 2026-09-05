export const TIPO_TODOS = 'TODOS'
export const TIPO_FOLGUISTA = 'FOLGUISTA'
export const OPCAO_TODAS_BASES = '__TODAS_BASES__'

function normalizarTexto(texto) {
  return String(texto || '')
    .trim()
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toUpperCase()
}

// Uma equipe pode ter vagas de varias disciplinas (TIPO EQUIPE) ao mesmo
// tempo — a equipe Folguista de uma base, por exemplo, pode ter vagas de
// construcao e de poda juntas. Por isso o tipo nao e mais um valor unico por
// equipe: ver tiposDaEquipe/ehEquipeFolguista, que sao independentes entre si.
export function ehEquipeFolguista(equipe) {
  if (typeof equipe?.folguista === 'boolean') {
    return equipe.folguista
  }
  // formato antigo da API (sem o campo 'folguista'): cai no prefixo
  return normalizarTexto(equipe?.prefixo) === TIPO_FOLGUISTA
}

export function tiposDaEquipe(equipe) {
  return Array.isArray(equipe?.tipos) ? equipe.tipos : []
}

export function equipeCombinaComTipo(equipe, tipoFiltro) {
  if (!tipoFiltro || tipoFiltro === TIPO_TODOS) {
    return true
  }
  if (tipoFiltro === TIPO_FOLGUISTA) {
    return ehEquipeFolguista(equipe)
  }
  return tiposDaEquipe(equipe).includes(tipoFiltro)
}

function rotuloTipo(tipo) {
  return tipo
    .toLowerCase()
    .split(' ')
    .map(parte => parte.charAt(0).toUpperCase() + parte.slice(1))
    .join(' ')
}

// Monta as opcoes do filtro de tipo a partir das disciplinas que existem de
// fato nas equipes carregadas, em vez de uma lista fixa — assim uma
// disciplina nova (cadastrada pela planilha) aparece no filtro sem precisar
// mexer no codigo.
export function opcoesTipoFiltro(equipes) {
  const disciplinas = new Set()

  for (const equipe of equipes || []) {
    for (const tipo of tiposDaEquipe(equipe)) {
      if (tipo) {
        disciplinas.add(tipo)
      }
    }
  }

  return [
    { label: 'Todos os tipos', value: TIPO_TODOS },
    ...[...disciplinas].sort().map(tipo => ({ label: rotuloTipo(tipo), value: tipo })),
    { label: 'Folguista', value: TIPO_FOLGUISTA }
  ]
}

// ------------------------------------------------------------
// Filtro de base com a opcao "Todas as bases", compartilhado entre telas
// ------------------------------------------------------------

export function normalizarSelecaoBases(bases) {
  if (!Array.isArray(bases)) {
    return []
  }

  const valores = [...new Set(bases.filter(Boolean))]

  if (valores.includes(OPCAO_TODAS_BASES)) {
    return [OPCAO_TODAS_BASES]
  }

  return valores
}

// Ao marcar "Todas as bases" com outras ja selecionadas, o esperado e que
// as outras saiam da selecao (nao o contrario).
export function proximaSelecaoBases(selecaoAtual, novaSelecao) {
  const selecao = Array.isArray(novaSelecao) ? novaSelecao : []

  if (
    selecao.includes(OPCAO_TODAS_BASES) &&
    selecaoAtual.includes(OPCAO_TODAS_BASES) &&
    selecao.length > 1
  ) {
    return selecao.filter(base => base !== OPCAO_TODAS_BASES)
  }

  return normalizarSelecaoBases(selecao)
}

export function equipeNaSelecaoDeBases(equipe, selecao) {
  if (!selecao.length || selecao.includes(OPCAO_TODAS_BASES)) {
    return true
  }

  return selecao.includes(String(equipe?.base || '').trim())
}
