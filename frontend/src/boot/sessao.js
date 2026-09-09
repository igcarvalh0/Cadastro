import { defineBoot } from '#q-app'

import { ROTA_LOGIN } from '../router'
import { useSessao } from '../composables/useSessao'

/**
 * A sessão expira em 12 horas, e o servidor pode ser reiniciado. Quando isso
 * acontece no meio do uso, toda chamada de API passa a responder 401 e cada
 * tela mostraria um erro genérico do tipo "não foi possível carregar".
 *
 * Em vez de tratar isso em cada uma das chamadas espalhadas pelas páginas, o
 * fetch é envelopado uma única vez aqui: qualquer 401 vindo da API manda a
 * pessoa para o login, guardando a tela em que ela estava.
 */
export default defineBoot(({ router }) => {
  const { marcarSessaoExpirada } = useSessao()
  const fetchOriginal = window.fetch.bind(window)

  window.fetch = async (recurso, opcoes) => {
    const resposta = await fetchOriginal(recurso, opcoes)

    const url = typeof recurso === 'string' ? recurso : recurso?.url || ''
    const ehChamadaDaApi = url.includes('/api/')

    // /api/sessao responde 200 mesmo deslogado: não é sinal de expiração
    const ehConsultaDeSessao = url.includes('/api/sessao')

    if (resposta.status === 401 && ehChamadaDaApi && !ehConsultaDeSessao) {
      marcarSessaoExpirada()

      const atual = router.currentRoute.value

      if (atual.path !== ROTA_LOGIN) {
        router.replace({
          path: ROTA_LOGIN,
          query: { destino: atual.fullPath, expirou: '1' }
        })
      }
    }

    return resposta
  }
})
