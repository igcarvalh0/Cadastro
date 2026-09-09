import { defineRouter } from '#q-app'
import { routes, handleHotUpdate } from 'vue-router/auto-routes'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory
} from 'vue-router'

import { useSessao } from '../composables/useSessao'

export const ROTA_LOGIN = '/login'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter((/* { store, ssrContext } */) => {
  const createHistory = import.meta.env.QUASAR_SERVER
    ? createMemoryHistory
    : import.meta.env.QUASAR_VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(import.meta.env.QUASAR_VUE_ROUTER_BASE)
  })

  // enable HMR for it
  if (import.meta.hot) {
    handleHotUpdate(Router)
  }

  // Sem sessão, só a tela de login abre. Com sessão, /login redireciona para
  // o início — não faz sentido ver o formulário já logado.
  Router.beforeEach(async destino => {
    const { garantirSessao, temPermissao } = useSessao()
    const usuario = await garantirSessao()

    if (destino.path === ROTA_LOGIN) {
      return usuario ? { path: '/' } : true
    }

    if (!usuario) {
      // guarda o destino para voltar até ele depois de entrar
      return { path: ROTA_LOGIN, query: { destino: destino.fullPath } }
    }

    const exigida = destino.meta?.permissao

    if (exigida && !temPermissao(exigida)) {
      return { path: '/' }
    }

    return true
  })

  return Router
})
