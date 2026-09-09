<template>
  <q-header elevated class="site-header text-white">
    <q-toolbar>
      <div class="site-logo q-mr-sm">
        <img src="/icons/favicon-128x128.png" alt="CGB Energia" />
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
            v-for="pagina in paginasPermitidas"
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

      <!-- ============================================== -->
      <!-- USUÁRIO LOGADO -->
      <!-- ============================================== -->

      <q-btn-dropdown
        v-if="usuario"
        flat
        no-caps
        auto-close
        class="q-ml-sm"
        :label="usuario.usuario"
        icon="account_circle"
        aria-label="Conta"
      >
        <q-list>
          <q-item>
            <q-item-section>
              <q-item-label class="text-weight-medium">
                {{ usuario.nome }}
              </q-item-label>
              <q-item-label caption>{{ usuario.nivel_rotulo }}</q-item-label>
            </q-item-section>
          </q-item>

          <q-separator />

          <q-item v-close-popup clickable @click="abrirTrocaSenha">
            <q-item-section avatar>
              <q-icon name="key" />
            </q-item-section>
            <q-item-section>Trocar minha senha</q-item-section>
          </q-item>

          <q-item v-close-popup clickable @click="encerrar">
            <q-item-section avatar>
              <q-icon name="logout" />
            </q-item-section>
            <q-item-section>Sair</q-item-section>
          </q-item>
        </q-list>
      </q-btn-dropdown>
    </q-toolbar>
  </q-header>

  <!-- ================================================== -->
  <!-- TROCA DE SENHA -->
  <!-- ================================================== -->

  <q-dialog v-model="dialogSenha">
    <q-card style="width: 100%; max-width: 380px">
      <q-card-section class="row items-center q-pb-sm">
        <div class="text-h6">Trocar minha senha</div>
        <q-space />
        <q-btn v-close-popup flat round dense icon="close" />
      </q-card-section>

      <q-separator />

      <q-card-section class="q-gutter-md">
        <q-banner v-if="erroSenha" dense class="bg-red-1 text-negative" rounded>
          {{ erroSenha }}
        </q-banner>

        <q-banner v-if="okSenha" dense class="bg-green-1 text-positive" rounded>
          {{ okSenha }}
        </q-banner>

        <q-input
          v-model="senhaAtual"
          outlined
          dense
          type="password"
          autocomplete="current-password"
          label="Senha atual"
        />

        <q-input
          v-model="senhaNova"
          outlined
          dense
          type="password"
          autocomplete="new-password"
          label="Nova senha"
          hint="Mínimo de 6 caracteres"
        />

        <q-input
          v-model="senhaConfirma"
          outlined
          dense
          type="password"
          autocomplete="new-password"
          label="Repita a nova senha"
        />
      </q-card-section>

      <q-separator />

      <q-card-actions align="right">
        <q-btn v-close-popup flat label="Cancelar" />
        <q-btn
          color="primary"
          label="Salvar"
          :loading="salvandoSenha"
          :disable="!senhaAtual || !senhaNova || !senhaConfirma"
          @click="salvarSenha"
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import { useRoute, useRouter } from 'vue-router'
import { useModoNoturno } from '../composables/useModoNoturno'
import {
  PODE_GERENCIAR_USUARIOS,
  PODE_GERENCIAR_VAGAS,
  PODE_VER_EQUIPES,
  PODE_VER_RESUMO,
  useSessao
} from '../composables/useSessao'

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
const { usuario, temPermissao, sair } = useSessao()

const PAGINAS = [
  {
    titulo: 'Resumo',
    rota: '/',
    caminhos: ['/', '/resumo'],
    icone: 'assessment',
    permissao: PODE_VER_RESUMO
  },
  {
    titulo: 'Banco de Dados',
    rota: '/banco-dados',
    caminhos: ['/banco-dados'],
    icone: 'storage',
    permissao: PODE_VER_EQUIPES
  },
  {
    titulo: 'Vagas',
    rota: '/cadastro-vagas',
    caminhos: ['/cadastro-vagas'],
    icone: 'assignment',
    permissao: PODE_GERENCIAR_VAGAS
  },
  {
    titulo: 'Usuários',
    rota: '/usuarios',
    caminhos: ['/usuarios'],
    icone: 'manage_accounts',
    permissao: PODE_GERENCIAR_USUARIOS
  }
]

// o menu mostra só o que o nível da pessoa alcança
const paginasPermitidas = computed(() =>
  PAGINAS.filter(pagina => temPermissao(pagina.permissao))
)

function ehPaginaAtual(pagina) {
  return pagina.caminhos.includes(route.path)
}

function navegar(pagina) {
  if (!ehPaginaAtual(pagina)) {
    router.push(pagina.rota)
  }
}

async function encerrar() {
  await sair()
  router.replace('/login')
}

// ============================================================
// TROCA DE SENHA
// ============================================================

const dialogSenha = ref(false)
const senhaAtual = ref('')
const senhaNova = ref('')
const senhaConfirma = ref('')
const salvandoSenha = ref(false)
const erroSenha = ref('')
const okSenha = ref('')

function abrirTrocaSenha() {
  senhaAtual.value = ''
  senhaNova.value = ''
  senhaConfirma.value = ''
  erroSenha.value = ''
  okSenha.value = ''
  dialogSenha.value = true
}

async function salvarSenha() {
  erroSenha.value = ''
  okSenha.value = ''

  if (senhaNova.value !== senhaConfirma.value) {
    erroSenha.value = 'A nova senha e a repetição não conferem.'
    return
  }

  salvandoSenha.value = true

  try {
    const resposta = await fetch('/api/minha-senha', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        senha_atual: senhaAtual.value,
        senha_nova: senhaNova.value
      })
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Não foi possível alterar a senha.')
    }

    okSenha.value = 'Senha alterada.'
    senhaAtual.value = ''
    senhaNova.value = ''
    senhaConfirma.value = ''
  } catch (e) {
    erroSenha.value = e.message || 'Não foi possível alterar a senha.'
  } finally {
    salvandoSenha.value = false
  }
}

onMounted(restaurarModoNoturno)
</script>
