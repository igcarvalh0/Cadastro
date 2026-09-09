import { defineBoot } from '#q-app'

import { useModoNoturno } from '../composables/useModoNoturno'

/**
 * Aplica o tema salvo antes da primeira tela montar.
 *
 * As páginas já restauram o tema no onMounted, mas isso acontece depois de um
 * primeiro desenho: quem estava no modo noturno via um piscar de tela clara
 * antes disso. Aqui é o ponto mais cedo em que dá para agir.
 */
export default defineBoot(() => {
  useModoNoturno().restaurarModoNoturno()
})
