<template>
  <q-header elevated class="site-header text-white">
    <q-toolbar>
      <div class="site-logo q-mr-sm">
        <img src="/icons/favicon-128x128.png" alt="Logo" />
      </div>

      <q-toolbar-title> {{ titulo }} </q-toolbar-title>

      <q-btn
        flat
        round
        dense
        icon="refresh"
        aria-label="Atualizar"
        :loading="carregando"
        @click="emit('atualizar')"
      >
        <q-tooltip>Atualizar</q-tooltip>
      </q-btn>

      <q-btn
        flat
        round
        dense
        :icon="modoNoturno ? 'light_mode' : 'dark_mode'"
        :aria-label="modoNoturno ? 'Ativar modo claro' : 'Ativar modo noturno'"
        @click="alternarModoNoturno"
      >
        <q-tooltip>{{ modoNoturno ? 'Modo claro' : 'Modo noturno' }}</q-tooltip>
      </q-btn>

      <q-btn-dropdown
        flat
        icon="menu"
        label="Menu"
        aria-label="Menu de navegação"
        auto-close
        class="q-ml-sm"
      >
        <q-list>
          <q-item
            v-for="pagina in PAGINAS"
            :key="pagina.rota"
            v-close-popup
            clickable
            :active="ehPaginaAtual(pagina)"
            active-class="text-primary text-weight-bold"
            @click="navegar(pagina)"
          >
            <q-item-section avatar>
              <q-icon :name="pagina.icone" />
            </q-item-section>

            <q-item-section>
              {{ pagina.titulo }}
            </q-item-section>
          </q-item>
        </q-list>
      </q-btn-dropdown>
    </q-toolbar>
  </q-header>
</template>

<script setup>
import { onMounted } from 'vue'

import { useRoute, useRouter } from 'vue-router'
import { useModoNoturno } from '../composables/useModoNoturno'

defineProps({
  titulo: {
    type: String,
    required: true
  },
  carregando: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['atualizar'])

const router = useRouter()
const route = useRoute()
const { modoNoturno, alternarModoNoturno, restaurarModoNoturno } = useModoNoturno()

const PAGINAS = [
  { titulo: 'Resumo', rota: '/', caminhos: ['/', '/resumo'], icone: 'assessment' },
  {
    titulo: 'Banco de Dados',
    rota: '/banco-dados',
    caminhos: ['/banco-dados'],
    icone: 'storage'
  },
  {
    titulo: 'Vagas',
    rota: '/cadastro-vagas',
    caminhos: ['/cadastro-vagas'],
    icone: 'assignment'
  }
]

function ehPaginaAtual(pagina) {
  return pagina.caminhos.includes(route.path)
}

function navegar(pagina) {
  if (!ehPaginaAtual(pagina)) {
    router.push(pagina.rota)
  }
}

onMounted(restaurarModoNoturno)
</script>
