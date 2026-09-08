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
    // nome de tipo de equipe sempre em caixa alta
    ...[...disciplinas].sort().map(tipo => ({ label: tipo.toUpperCase(), value: tipo })),
    { label: TIPO_FOLGUISTA, value: TIPO_FOLGUISTA }
  ]
}

// ------------------------------------------------------------
// Filtro de setor
// ------------------------------------------------------------

export const SETOR_TODOS = 'TODOS'

// O setor e informado por disciplina, entao uma equipe com vagas de construcao
// e de poda pode responder a dois setores. O filtro casa se QUALQUER vaga dela
// for do setor escolhido.
export function setoresDaEquipe(equipe) {
  return Array.isArray(equipe?.setores) ? equipe.setores : []
}

export function equipeCombinaComSetor(equipe, setorFiltro) {
  if (!setorFiltro || setorFiltro === SETOR_TODOS) {
    return true
  }

  return setoresDaEquipe(equipe).includes(setorFiltro)
}

export function opcoesSetorFiltro(equipes) {
  const setores = new Set()

  for (const equipe of equipes || []) {
    for (const setor of setoresDaEquipe(equipe)) {
      if (setor) {
        setores.add(setor)
      }
    }
  }

  return [
    { label: 'Todos os setores', value: SETOR_TODOS },
    ...[...setores].sort().map(setor => ({ label: setor, value: setor }))
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

// ============================================================
// FUNÇÕES DOS COLABORADORES
// ============================================================

// Espelha ORDEM_FUNCOES e padronizar_funcao do app.py, na mesma ordem de
// exibição. Se mudar a regra lá, mudar aqui também.
export const FUNCOES_SISTEMA = [
  'ENCARREGADO',
  'ELETRICISTA',
  'MOTORISTA',
  'AUXILIAR DE ELETRICISTA',
  'PODADOR'
]

// O cadastro traz nomes detalhados ("MOTORISTA OP DE GUINCHO", "ENCARREGADO
// DE PODA", "ELETRICISTA MONTADOR"), então a regra é por palavra contida.
export function padronizarFuncao(funcao) {
  const original = String(funcao || '').trim().toUpperCase()

  if (!original) {
    return ''
  }

  const semAcento = original.normalize('NFD').replace(/[\u0300-\u036f]/g, '')

  if (semAcento.includes('ENCARREGADO')) {
    return 'ENCARREGADO'
  }

  if (semAcento.includes('MOTORISTA')) {
    return 'MOTORISTA'
  }

  // precisa das duas palavras: existem AUXILIAR ADMINISTRATIVO, AUXILIAR DE
  // ALMOXARIFADO e outros que não têm nada a ver com eletricista
  if (semAcento.includes('AUXILIAR') && semAcento.includes('ELETRICISTA')) {
    return 'AUXILIAR DE ELETRICISTA'
  }

  if (semAcento.includes('ELETRICISTA')) {
    return 'ELETRICISTA'
  }

  if (semAcento.includes('PODADOR')) {
    return 'PODADOR'
  }

  return original
}
