<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page class="tela-login flex flex-center q-pa-md">
        <q-card bordered class="cartao-login">
          <q-card-section class="text-center q-pb-none">
            <div class="marca-login">
              <img src="/icons/favicon-128x128.png" alt="CGB Energia" />
            </div>

            <div class="text-h5 q-mt-md titulo-login">
              Gerenciador de Equipes
            </div>

            <div class="text-caption text-grey-7">
              Entre com o seu usuário para continuar
            </div>
          </q-card-section>

          <q-card-section>
            <q-banner
              v-if="sessaoExpirou"
              dense
              class="bg-orange-1 text-orange-9 q-mb-md"
              rounded
            >
              Sua sessão expirou. Entre novamente para continuar.
            </q-banner>

            <q-banner v-if="erro" dense class="bg-red-1 text-negative q-mb-md" rounded>
              {{ erro }}
            </q-banner>

            <q-form class="q-gutter-md" @submit.prevent="autenticar">
              <q-input
                v-model="login"
                outlined
                dense
                autofocus
                label="Usuário"
                autocomplete="username"
                :disable="entrando"
              >
                <template #prepend>
                  <q-icon name="person" />
                </template>
              </q-input>

              <q-input
                v-model="senha"
                outlined
                dense
                label="Senha"
                autocomplete="current-password"
                :type="mostrarSenha ? 'text' : 'password'"
                :disable="entrando"
              >
                <template #prepend>
                  <q-icon name="lock" />
                </template>

                <template #append>
                  <q-icon
                    class="cursor-pointer"
                    :name="mostrarSenha ? 'visibility_off' : 'visibility'"
                    @click="mostrarSenha = !mostrarSenha"
                  >
                    <q-tooltip>
                      {{ mostrarSenha ? 'Ocultar senha' : 'Mostrar senha' }}
                    </q-tooltip>
                  </q-icon>
                </template>
              </q-input>

              <q-btn
                type="submit"
                color="primary"
                class="full-width"
                label="Entrar"
                :loading="entrando"
                :disable="!login || !senha"
              />
            </q-form>
          </q-card-section>

          <q-card-section class="text-center q-pt-none">
            <q-btn
              flat
              dense
              size="sm"
              :icon="modoNoturno ? 'light_mode' : 'dark_mode'"
              :label="modoNoturno ? 'Modo claro' : 'Modo noturno'"
              @click="alternarModoNoturno"
            />
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useModoNoturno } from '../composables/useModoNoturno'
import { useSessao } from '../composables/useSessao'

const router = useRouter()
const route = useRoute()
const { entrar } = useSessao()
const { modoNoturno, alternarModoNoturno, restaurarModoNoturno } = useModoNoturno()

const login = ref('')
const senha = ref('')
const mostrarSenha = ref(false)
const entrando = ref(false)
const erro = ref('')

// marcado pelo boot quando a API respondeu 401 no meio do uso
const sessaoExpirou = computed(() => route.query.expirou === '1')

async function autenticar() {
  erro.value = ''
  entrando.value = true

  try {
    await entrar(login.value.trim(), senha.value)

    // volta para a tela que a pessoa tentou abrir antes do login
    const destino = route.query.destino
    await router.replace(
      typeof destino === 'string' && destino !== '/login' ? destino : '/'
    )
  } catch (e) {
    erro.value = e.message || 'Não foi possível entrar.'
    senha.value = ''
  } finally {
    entrando.value = false
  }
}

onMounted(restaurarModoNoturno)
</script>

<style scoped>
.tela-login {
  background: var(--fundo);
  min-height: 100vh;
}

.cartao-login {
  width: 100%;
  max-width: 399px; /* 380px + 5% */
  background: var(--superficie);
  box-shadow: var(--sombra);
}

.titulo-login {
  font-family: var(--fonte-ui);
  font-weight: 700;
  color: var(--titulo);
}

.marca-login img {
  /* a arte e um logo largo (1512x596px), nao um icone quadrado: largura fixa
     estica o desenho. Altura fixa + largura automatica preserva a proporcao
     real do arquivo, entao nunca distorce, mesmo se a arte for trocada. */
  height: 70.4px;
  width: auto;
}
</style>
