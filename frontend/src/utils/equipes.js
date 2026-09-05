export const TIPO_TODOS = 'TODOS'
export const TIPO_CONSTRUCAO = 'CONSTRUÇÃO'
export const TIPO_FOLGUISTA = 'FOLGUISTA'

export const OPCOES_TIPO = [
  { label: 'Todos os tipos', value: TIPO_TODOS },
  { label: 'Construção', value: TIPO_CONSTRUCAO },
  { label: 'Folguista', value: TIPO_FOLGUISTA }
]

// O tipo vem do backend (baseado na estrutura das vagas). O prefixo so e usado
// como reserva, para dados antigos que ainda nao trafegam o campo.
export function ehEquipeFolguista(equipe) {
  const normalizar = texto =>
    String(texto || '')
      .trim()
      .normalize('NFD')
      .replace(/\p{Diacritic}/gu, '')
      .toUpperCase()

  if (equipe?.tipo) {
    return normalizar(equipe.tipo) === TIPO_FOLGUISTA
  }

  return normalizar(equipe?.prefixo) === TIPO_FOLGUISTA
}

export function tipoDaEquipe(equipe) {
  return ehEquipeFolguista(equipe) ? TIPO_FOLGUISTA : TIPO_CONSTRUCAO
}
