import { ref } from 'vue'
import { Dark } from 'quasar'

const CHAVE_ARMAZENAMENTO = 'gerenciadorEquipes_modoNoturno'

// ============================================================
// FAVICON POR TEMA
// ============================================================

// O ícone da aba vive fora da página, então CSS não alcança ele — a troca
// precisa ser feita mexendo nas tags <link> do <head>.
//
// A alternativa declarativa (media="(prefers-color-scheme: dark)") seguiria o
// tema do sistema operacional, e não o botão de modo noturno daqui. Como o
// app tem botão próprio, quem manda é ele.
//
// Para trocar as artes, basta substituir os arquivos:
//   public/icons/favicon-*.png        e  public/favicon.ico        (tema claro)
//   public/icons/favicon-*-escuro.png e  public/favicon-escuro.ico (tema escuro)
const ICONES = {
  claro: [
    { sizes: '128x128', type: 'image/png', href: '/icons/favicon-128x128.png' },
    { sizes: '96x96', type: 'image/png', href: '/icons/favicon-96x96.png' },
    { sizes: '32x32', type: 'image/png', href: '/icons/favicon-32x32.png' },
    { sizes: '16x16', type: 'image/png', href: '/icons/favicon-16x16.png' },
    { type: 'image/x-icon', href: '/favicon.ico' }
  ],
  escuro: [
    { sizes: '128x128', type: 'image/png', href: '/icons/favicon-128x128-escuro.png' },
    { sizes: '96x96', type: 'image/png', href: '/icons/favicon-96x96-escuro.png' },
    { sizes: '32x32', type: 'image/png', href: '/icons/favicon-32x32-escuro.png' },
    { sizes: '16x16', type: 'image/png', href: '/icons/favicon-16x16-escuro.png' },
    { type: 'image/x-icon', href: '/favicon-escuro.ico' }
  ]
}

let temaDoFaviconAplicado = null

function aplicarFavicon(escuro) {
  const tema = escuro ? 'escuro' : 'claro'

  // trocar as tags à toa faz o navegador rebaixar o ícone por um instante
  if (tema === temaDoFaviconAplicado || typeof document === 'undefined') {
    return
  }

  temaDoFaviconAplicado = tema

  for (const antigo of document.querySelectorAll('link[rel="icon"]')) {
    antigo.remove()
  }

  for (const icone of ICONES[tema]) {
    const link = document.createElement('link')

    link.rel = 'icon'
    link.type = icone.type

    if (icone.sizes) {
      link.sizes = icone.sizes
    }

    // o sufixo força o navegador a reler o arquivo em vez de repetir o que
    // ele já tinha em cache para aquele endereço
    link.href = `${icone.href}?tema=${tema}`

    document.head.append(link)
  }
}

// ============================================================
// TEMA
// ============================================================

export function useModoNoturno() {
  const modoNoturno = ref(Dark.isActive)

  function definirModo(ativo) {
    modoNoturno.value = ativo
    Dark.set(ativo)
    aplicarFavicon(ativo)
  }

  function alternarModoNoturno() {
    definirModo(!modoNoturno.value)
    localStorage.setItem(CHAVE_ARMAZENAMENTO, String(modoNoturno.value))
  }

  function restaurarModoNoturno() {
    const modoSalvo = localStorage.getItem(CHAVE_ARMAZENAMENTO)

    definirModo(modoSalvo === null ? Dark.isActive : modoSalvo === 'true')
  }

  return { modoNoturno, alternarModoNoturno, restaurarModoNoturno }
}
