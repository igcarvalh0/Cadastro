<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="site-header text-white">
      <q-toolbar>
        <q-btn flat round dense icon="arrow_back" @click="voltar" />

        <div class="site-logo q-mr-sm">
          <img src="/icons/favicon-128x128.png" alt="Logo" />
        </div>

        <q-toolbar-title> Cadastro de Vagas </q-toolbar-title>

        <q-btn
          flat
          round
          dense
          :icon="modoNoturno ? 'light_mode' : 'dark_mode'"
          :aria-label="
            modoNoturno ? 'Ativar modo claro' : 'Ativar modo noturno'
          "
          @click="alternarModoNoturno"
        >
          <q-tooltip>{{
            modoNoturno ? 'Modo claro' : 'Modo noturno'
          }}</q-tooltip>
        </q-btn>

        <q-btn flat label="Banco de Dados" @click="irParaBanco" />

        <q-btn flat label="Resumo" @click="irParaResumo" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-md">
        <!-- ================================================== -->
        <!-- CABEÇALHO -->
        <!-- ================================================== -->

        <div class="row items-center q-mb-md">
          <div class="col">
            <div class="text-h5"> Cadastro de Vagas </div>

            <div class="text-subtitle2 text-grey-7">
              Criação de equipes e das vagas disponíveis para alocação
            </div>
          </div>

          <div class="col-auto">
            <q-btn
              color="primary"
              icon="refresh"
              label="Atualizar"
              :loading="carregando"
              @click="carregarEquipes"
            />
          </div>
        </div>

        <q-banner v-if="erro" class="bg-red-1 text-negative q-mb-md" rounded>
          {{ erro }}
        </q-banner>

        <q-banner
          v-if="sucesso"
          class="bg-green-1 text-positive q-mb-md"
          rounded
        >
          {{ sucesso }}
        </q-banner>

        <!-- ================================================== -->
        <!-- FORMULÁRIOS -->
        <!-- ================================================== -->

        <div class="row q-col-gutter-md q-mb-md">
          <div class="col-12 col-md-6">
            <q-card bordered>
              <q-card-section class="text-center">
                <div class="text-h6"> Nova equipe </div>
              </q-card-section>

              <q-separator />

              <q-card-section class="q-gutter-md">
                <q-select
                  v-model="novaEquipeBase"
                  outlined
                  dense
                  use-input
                  fill-input
                  hide-selected
                  input-debounce="0"
                  new-value-mode="add-unique"
                  label="Base"
                  hint="Selecione uma base existente ou digite uma nova"
                  :options="basesFiltradas"
                  @filter="filtrarBases"
                />

                <q-input
                  v-model="novaEquipePrefixo"
                  outlined
                  dense
                  label="Prefixo"
                  hint="Ex.: MA-BCB-O007M ou Folguista"
                />

                <q-btn
                  color="primary"
                  icon="group_add"
                  label="Criar equipe"
                  :disable="!podeCriarEquipe"
                  :loading="salvandoEquipe"
                  @click="criarEquipe"
                />
              </q-card-section>
            </q-card>
          </div>

          <div class="col-12 col-md-6">
            <q-card bordered>
              <q-card-section class="text-center">
                <div class="text-h6"> Nova vaga </div>
              </q-card-section>

              <q-separator />

              <q-card-section class="q-gutter-md">
                <q-select
                  v-model="vagaEquipe"
                  outlined
                  dense
                  use-input
                  fill-input
                  hide-selected
                  emit-value
                  map-options
                  input-debounce="0"
                  label="Equipe"
                  :options="equipesOpcoesFiltradas"
                  @filter="filtrarEquipesOpcoes"
                />

                <q-select
                  v-model="vagaFuncao"
                  outlined
                  dense
                  label="Função da vaga"
                  :options="OPCOES_FUNCAO"
                />

                <q-select
                  v-model="vagaEstrutura"
                  outlined
                  dense
                  label="Estrutura"
                  :options="OPCOES_ESTRUTURA"
                />

                <q-btn
                  color="primary"
                  icon="add"
                  label="Adicionar vaga"
                  :disable="!podeCriarVaga"
                  :loading="salvandoVaga"
                  @click="criarVaga"
                />
              </q-card-section>
            </q-card>
          </div>
        </div>

        <!-- ================================================== -->
        <!-- VAGAS CADASTRADAS -->
        <!-- ================================================== -->

        <q-card bordered>
          <q-card-section class="text-center">
            <div class="text-h6"> Vagas cadastradas </div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <q-input
              v-model="filtroEquipe"
              outlined
              dense
              clearable
              placeholder="Pesquisar por prefixo ou base..."
            >
              <template #prepend>
                <q-icon name="search" />
              </template>
            </q-input>
          </q-card-section>

          <div v-if="carregando" class="row justify-center q-pa-xl">
            <q-spinner color="primary" size="50px" />
          </div>

          <q-list v-else separator>
            <div
              v-if="!equipesFiltradas.length"
              class="text-grey-7 q-pa-md text-center"
            >
              Nenhuma equipe encontrada.
            </div>

            <q-expansion-item
              v-for="equipe in equipesFiltradas"
              :key="equipe.id"
              expand-separator
              :label="equipe.prefixo || 'Equipe'"
              :caption="`${equipe.base || ''} — ${equipe.vagas.length} vaga(s)`"
            >
              <q-card flat>
                <q-card-section class="q-pb-none text-right">
                  <q-btn
                    outline
                    dense
                    color="negative"
                    icon="delete_forever"
                    label="Excluir equipe"
                    size="sm"
                    :disable="equipe.vagas.some(vaga => vaga.ocupada)"
                    @click="removerEquipe(equipe)"
                  >
                    <q-tooltip v-if="equipe.vagas.some(vaga => vaga.ocupada)">
                      Remova os colaboradores alocados antes de excluir a equipe
                    </q-tooltip>
                  </q-btn>
                </q-card-section>

                <q-card-section>
                  <div v-if="!equipe.vagas.length" class="text-grey-7">
                    Nenhuma vaga cadastrada nesta equipe.
                  </div>

                  <q-list v-else separator>
                    <q-item v-for="vaga in equipe.vagas" :key="vaga.id">
                      <q-item-section>
                        <q-item-label class="text-weight-medium">
                          {{ vaga.funcao_er || 'Função não informada' }}
                        </q-item-label>

                        <q-item-label caption>
                          {{
                            vaga.colaborador
                              ? `${vaga.colaborador.chapa} — ${vaga.colaborador.nome}`
                              : 'Sem colaborador alocado'
                          }}
                        </q-item-label>
                      </q-item-section>

                      <q-item-section side>
                        <div class="row items-center no-wrap">
                          <q-chip
                            v-if="vaga.ocupada"
                            color="positive"
                            text-color="white"
                            size="sm"
                          >
                            OCUPADA
                          </q-chip>

                          <q-chip
                            v-else
                            color="grey-6"
                            text-color="white"
                            size="sm"
                          >
                            LIVRE
                          </q-chip>

                          <q-btn
                            flat
                            round
                            dense
                            color="negative"
                            icon="delete"
                            class="q-ml-sm"
                            aria-label="Excluir vaga"
                            :disable="vaga.ocupada"
                            @click="removerVaga(vaga)"
                          >
                            <q-tooltip v-if="vaga.ocupada">
                              Remova o colaborador antes de excluir a vaga
                            </q-tooltip>
                          </q-btn>
                        </div>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-card-section>
              </q-card>
            </q-expansion-item>
          </q-list>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

import { useRouter } from 'vue-router'
import { useModoNoturno } from '../composables/useModoNoturno'

const router = useRouter()
const { modoNoturno, alternarModoNoturno, restaurarModoNoturno } = useModoNoturno()

const OPCOES_FUNCAO = [
  'ENCARREGADO',
  'ELETRICISTA',
  'MOTORISTA',
  'AUXILIAR DE ELETRICISTA'
]

const OPCOES_ESTRUTURA = ['Construção', 'Folguista']

// ============================================================
// ESTADO
// ============================================================

const equipes = ref([])

const carregando = ref(false)

const erro = ref('')
const sucesso = ref('')

const novaEquipeBase = ref(null)
const novaEquipePrefixo = ref('')
const salvandoEquipe = ref(false)

const vagaEquipe = ref(null)
const vagaFuncao = ref(null)
const vagaEstrutura = ref(OPCOES_ESTRUTURA[0])
const salvandoVaga = ref(false)

const filtroEquipe = ref('')

const basesFiltradas = ref([])
const equipesOpcoesFiltradas = ref([])

// ============================================================
// DERIVADOS
// ============================================================

const bases = computed(() => {
  const valores = new Set()

  equipes.value.forEach(equipe => {
    if (equipe.base) {
      valores.add(equipe.base)
    }
  })

  return [...valores].sort()
})

const equipesOpcoes = computed(() =>
  equipes.value.map(equipe => ({
    label: `${equipe.prefixo} — ${equipe.base}`,
    value: equipe.id
  }))
)

const equipesFiltradas = computed(() => {
  const termo = (filtroEquipe.value || '').trim().toLowerCase()

  if (!termo) {
    return equipes.value
  }

  return equipes.value.filter(equipe =>
    `${equipe.prefixo} ${equipe.base}`.toLowerCase().includes(termo)
  )
})

const podeCriarEquipe = computed(() =>
  Boolean(
    (novaEquipeBase.value || '').trim() && novaEquipePrefixo.value.trim()
  )
)

const podeCriarVaga = computed(() =>
  Boolean(vagaEquipe.value && vagaFuncao.value && vagaEstrutura.value)
)

// ============================================================
// FILTROS DOS SELECTS
// ============================================================

function filtrarBases(termo, update) {
  update(() => {
    const busca = termo.toLowerCase()

    basesFiltradas.value = busca
      ? bases.value.filter(base => base.toLowerCase().includes(busca))
      : bases.value
  })
}

function filtrarEquipesOpcoes(termo, update) {
  update(() => {
    const busca = termo.toLowerCase()

    equipesOpcoesFiltradas.value = busca
      ? equipesOpcoes.value.filter(opcao =>
          opcao.label.toLowerCase().includes(busca)
        )
      : equipesOpcoes.value
  })
}

// ============================================================
// NAVEGAÇÃO
// ============================================================

function voltar() {
  router.back()
}

function irParaBanco() {
  router.push('/')
}

function irParaResumo() {
  router.push('/resumo')
}

// ============================================================
// AÇÕES
// ============================================================

async function carregarEquipes() {
  carregando.value = true

  try {
    const resposta = await fetch('/api/equipes')
    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao carregar as equipes.')
    }

    equipes.value = dados
  } catch (e) {
    erro.value = e.message || 'Erro ao carregar as equipes.'
  } finally {
    carregando.value = false
  }
}

async function criarEquipe() {
  erro.value = ''
  sucesso.value = ''
  salvandoEquipe.value = true

  try {
    const resposta = await fetch('/api/equipes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        base: novaEquipeBase.value,
        prefixo: novaEquipePrefixo.value
      })
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao criar a equipe.')
    }

    sucesso.value = `Equipe ${dados.equipe.prefixo} criada com sucesso.`
    novaEquipePrefixo.value = ''

    await carregarEquipes()
    vagaEquipe.value = dados.equipe.id
  } catch (e) {
    erro.value = e.message || 'Erro ao criar a equipe.'
  } finally {
    salvandoEquipe.value = false
  }
}

async function criarVaga() {
  erro.value = ''
  sucesso.value = ''
  salvandoVaga.value = true

  try {
    const resposta = await fetch('/api/equipes/vagas', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        equipe_id: vagaEquipe.value,
        funcao_er: vagaFuncao.value,
        estrutura: vagaEstrutura.value
      })
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao criar a vaga.')
    }

    sucesso.value = `Vaga de ${dados.vaga.funcao_er} adicionada com sucesso.`
    vagaFuncao.value = null

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao criar a vaga.'
  } finally {
    salvandoVaga.value = false
  }
}

async function removerVaga(vaga) {
  if (!window.confirm('Deseja realmente excluir esta vaga?')) {
    return
  }

  erro.value = ''
  sucesso.value = ''

  try {
    const resposta = await fetch(`/api/equipes/vagas/${vaga.id}`, {
      method: 'DELETE'
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao excluir a vaga.')
    }

    sucesso.value = 'Vaga excluída com sucesso.'

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao excluir a vaga.'
  }
}

async function removerEquipe(equipe) {
  if (
    !window.confirm(
      `Deseja realmente excluir a equipe ${equipe.prefixo} e todas as suas vagas?`
    )
  ) {
    return
  }

  erro.value = ''
  sucesso.value = ''

  try {
    const resposta = await fetch(`/api/equipes/${equipe.id}`, {
      method: 'DELETE'
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao excluir a equipe.')
    }

    sucesso.value = `Equipe ${equipe.prefixo} excluída com sucesso.`

    if (vagaEquipe.value === equipe.id) {
      vagaEquipe.value = null
    }

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao excluir a equipe.'
  }
}

// ============================================================
// INICIALIZAÇÃO
// ============================================================

watch(vagaEquipe, id => {
  const equipe = equipes.value.find(item => item.id === id)

  if (!equipe) {
    return
  }

  vagaEstrutura.value =
    (equipe.prefixo || '').trim().toUpperCase() === 'FOLGUISTA'
      ? 'Folguista'
      : 'Construção'
})

onMounted(() => {
  restaurarModoNoturno()
  carregarEquipes()
})
</script>
