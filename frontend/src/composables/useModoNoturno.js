import { ref } from 'vue'
import { Dark } from 'quasar'

const CHAVE_ARMAZENAMENTO = 'gerenciadorEquipes_modoNoturno'

export function useModoNoturno() {
  const modoNoturno = ref(Dark.isActive)

  function alternarModoNoturno() {
    modoNoturno.value = !modoNoturno.value
    Dark.set(modoNoturno.value)
    localStorage.setItem(CHAVE_ARMAZENAMENTO, String(modoNoturno.value))
  }

  function restaurarModoNoturno() {
    const modoSalvo = localStorage.getItem(CHAVE_ARMAZENAMENTO)

    if (modoSalvo !== null) {
      modoNoturno.value = modoSalvo === 'true'
      Dark.set(modoNoturno.value)
    }
  }

  return { modoNoturno, alternarModoNoturno, restaurarModoNoturno }
}
