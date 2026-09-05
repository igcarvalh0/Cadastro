<template>
  <q-layout view="lHh Lpr lFf">
    <CabecalhoApp
      titulo="Cadastro de Vagas"
      :carregando="carregando"
      @atualizar="carregarEquipes"
    />

    <q-page-container>
      <q-page class="q-pa-md">
        <!-- ================================================== -->
        <!-- CABEÇALHO -->
        <!-- ================================================== -->

        <div class="q-mb-md">
          <div class="text-h5"> Cadastro de Vagas </div>

          <div class="text-subtitle2 text-grey-7">
            Criação de equipes e das vagas disponíveis para alocação
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
        <!-- PLANILHA EM MASSA -->
        <!-- ================================================== -->

        <q-card bordered class="q-mb-md">
          <q-card-section class="text-center">
            <div class="text-h6"> Cadastro em massa por planilha </div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <div class="row q-col-gutter-md items-start">
              <div class="col-12 col-md-4">
                <q-btn
                  outline
                  color="primary"
                  icon="download"
                  label="Baixar planilha"
                  :loading="baixandoPlanilha"
                  class="full-width"
                  @click="baixarPlanilha"
                />
                <div class="text-caption text-grey-7 q-mt-sm">
                  Traz as equipes de hoje, uma por linha, com a quantidade de
                  cada função.
                </div>
              </div>

              <div class="col-12 col-md">
                <q-file
                  v-model="arquivoPlanilha"
                  outlined
                  dense
                  clearable
                  accept=".xlsx"
                  label="Planilha preenchida (.xlsx)"
                >
                  <template #prepend>
                    <q-icon name="attach_file" />
                  </template>
                </q-file>

                <div class="text-caption text-grey-7 q-mt-sm">
                  Preencha a coluna AÇÃO com <strong>criar</strong>,
                  <strong>editar</strong> ou <strong>excluir</strong>. Linha sem
                  ação é ignorada.
                </div>
              </div>

              <div class="col-12 col-md-auto">
                <q-btn
                  color="primary"
                  icon="fact_check"
                  label="Conferir mudanças"
                  :disable="!arquivoPlanilha"
                  :loading="analisandoPlanilha"
                  @click="analisarPlanilha"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- ================================================== -->
        <!-- VAGAS CADASTRADAS -->
        <!-- ================================================== -->

        <q-card bordered>
          <q-card-section class="text-center">
            <div class="text-h6"> Vagas cadastradas </div>
          </q-card-section>

          <q-separator />

          <q-card-section>
            <div class="row q-col-gutter-md items-center">
              <div class="col-12 col-md-4">
                <q-select
                  v-model="baseFiltro"
                  outlined
                  dense
                  clearable
                  multiple
                  use-chips
                  label="Base"
                  :options="bases"
                />
              </div>

              <div class="col-12 col-md-3">
                <q-select
                  v-model="tipoFiltro"
                  outlined
                  dense
                  emit-value
                  map-options
                  label="Tipo"
                  :options="OPCOES_TIPO"
                />
              </div>

              <div class="col-12 col-md">
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
              </div>

              <div class="col-auto">
                <q-chip color="primary" text-color="white">
                  {{ equipesFiltradas.length }} equipe(s)
                </q-chip>
              </div>
            </div>
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
                <q-card-section class="q-pb-none">
                  <div class="row q-gutter-sm justify-end">
                    <q-btn
                      outline
                      dense
                      size="sm"
                      color="primary"
                      icon="edit"
                      label="Editar equipe"
                      @click="abrirEdicaoEquipe(equipe)"
                    />

                    <q-btn
                      outline
                      dense
                      size="sm"
                      color="negative"
                      icon="person_remove"
                      label="Remover todos os colaboradores"
                      :disable="!equipe.vagas.some(vaga => vaga.ocupada)"
                      @click="liberarEquipe(equipe)"
                    >
                      <q-tooltip v-if="!equipe.vagas.some(vaga => vaga.ocupada)">
                        Nenhum colaborador alocado nesta equipe
                      </q-tooltip>
                    </q-btn>

                    <q-btn
                      outline
                      dense
                      size="sm"
                      color="negative"
                      icon="delete_forever"
                      label="Excluir equipe"
                      :disable="equipe.vagas.some(vaga => vaga.ocupada)"
                      @click="removerEquipe(equipe)"
                    >
                      <q-tooltip v-if="equipe.vagas.some(vaga => vaga.ocupada)">
                        Remova os colaboradores alocados antes de excluir a
                        equipe
                      </q-tooltip>
                    </q-btn>
                  </div>
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

    <!-- ==================================================== -->
    <!-- EDIÇÃO DE EQUIPE -->
    <!-- ==================================================== -->

    <q-dialog v-model="dialogEdicao">
      <q-card style="min-width: 340px">
        <q-card-section>
          <div class="text-h6"> Editar equipe </div>
        </q-card-section>

        <q-separator />

        <q-card-section class="q-gutter-md">
          <q-select
            v-model="edicaoBase"
            outlined
            dense
            use-input
            fill-input
            hide-selected
            input-debounce="0"
            new-value-mode="add-unique"
            label="Base"
            :options="basesFiltradas"
            @filter="filtrarBases"
          />

          <q-input v-model="edicaoPrefixo" outlined dense label="Prefixo" />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn v-close-popup flat label="Cancelar" color="grey-7" />

          <q-btn
            color="primary"
            label="Salvar"
            :disable="!podeSalvarEdicao"
            :loading="salvandoEdicao"
            @click="salvarEdicaoEquipe"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- ==================================================== -->
    <!-- PRÉVIA DA PLANILHA -->
    <!-- ==================================================== -->

    <q-dialog v-model="dialogPlanilha">
      <q-card style="min-width: 560px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6"> Conferir mudanças </div>
          <div class="text-caption text-grey-7">
            Nada foi gravado ainda. Confira e confirme.
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section style="max-height: 60vh" class="scroll">
          <div v-if="planoPlanilha" class="q-gutter-md">
            <div class="row q-gutter-sm">
              <q-chip
                :color="planoPlanilha.criar.length ? 'positive' : 'grey-5'"
                text-color="white"
              >
                {{ planoPlanilha.criar.length }} a criar
              </q-chip>
              <q-chip
                :color="planoPlanilha.editar.length ? 'primary' : 'grey-5'"
                text-color="white"
              >
                {{ planoPlanilha.editar.length }} a editar
              </q-chip>
              <q-chip
                :color="planoPlanilha.excluir.length ? 'negative' : 'grey-5'"
                text-color="white"
              >
                {{ planoPlanilha.excluir.length }} a excluir
              </q-chip>
              <q-chip
                :color="planoPlanilha.erros.length ? 'negative' : 'grey-5'"
                text-color="white"
              >
                {{ planoPlanilha.erros.length }} com erro
              </q-chip>
              <q-chip color="grey-6" text-color="white">
                {{ planoPlanilha.ignoradas }} sem alteração
              </q-chip>
            </div>

            <q-banner
              v-if="planoPlanilha.erros.length"
              class="bg-red-1 text-negative"
              rounded
            >
              Corrija as linhas com erro antes de aplicar. Nada será gravado
              enquanto houver erro.
            </q-banner>

            <div v-if="planoPlanilha.erros.length">
              <div class="text-subtitle2 text-negative q-mb-xs"> Erros </div>
              <q-list bordered separator dense>
                <q-item v-for="e in planoPlanilha.erros" :key="'e' + e.linha">
                  <q-item-section>
                    <q-item-label>
                      Linha {{ e.linha }} — {{ e.equipe }}
                    </q-item-label>
                    <q-item-label caption class="text-negative">
                      {{ e.erro }}
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div v-if="planoPlanilha.criar.length">
              <div class="text-subtitle2 q-mb-xs"> Criar </div>
              <q-list bordered separator dense>
                <q-item v-for="i in planoPlanilha.criar" :key="'c' + i.linha">
                  <q-item-section>
                    <q-item-label>
                      {{ i.equipe }}
                      <q-badge
                        v-if="i.era_edicao"
                        color="orange"
                        text-color="white"
                        class="q-ml-sm"
                      >
                        equipe nova
                      </q-badge>
                    </q-item-label>
                    <q-item-label caption>
                      {{ i.total }} vaga(s):
                      {{
                        Object.entries(i.vagas)
                          .map(([f, q]) => q + ' ' + f)
                          .join(', ')
                      }}
                    </q-item-label>
                    <q-item-label v-if="i.era_edicao" caption class="text-orange-9">
                      A linha {{ i.linha }} está como "editar", mas essa equipe
                      ainda não existe — será criada.
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div v-if="planoPlanilha.editar.length">
              <div class="text-subtitle2 q-mb-xs"> Editar </div>
              <q-list bordered separator dense>
                <q-item v-for="i in planoPlanilha.editar" :key="'ed' + i.linha">
                  <q-item-section>
                    <q-item-label>{{ i.equipe }}</q-item-label>
                    <q-item-label caption>{{ i.resumo }}</q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>

            <div v-if="planoPlanilha.excluir.length">
              <div class="text-subtitle2 text-negative q-mb-xs"> Excluir </div>
              <q-list bordered separator dense>
                <q-item v-for="i in planoPlanilha.excluir" :key="'x' + i.linha">
                  <q-item-section>
                    <q-item-label>{{ i.equipe }}</q-item-label>
                    <q-item-label caption>
                      perde {{ i.vagas }} vaga(s) cadastrada(s)
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </q-card-section>

        <q-separator />

        <q-card-actions align="right">
          <q-btn v-close-popup flat label="Cancelar" color="grey-7" />

          <q-btn
            color="primary"
            label="Aplicar"
            :disable="!podeAplicarPlanilha"
            :loading="aplicandoPlanilha"
            @click="aplicarPlanilha"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

import CabecalhoApp from '../components/CabecalhoApp.vue'
import { ehEquipeFolguista, OPCOES_TIPO, TIPO_TODOS } from '../utils/equipes'

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
const baseFiltro = ref([])
const tipoFiltro = ref(TIPO_TODOS)

const arquivoPlanilha = ref(null)
const planoPlanilha = ref(null)
const dialogPlanilha = ref(false)
const baixandoPlanilha = ref(false)
const analisandoPlanilha = ref(false)
const aplicandoPlanilha = ref(false)

const dialogEdicao = ref(false)
const equipeEmEdicao = ref(null)
const edicaoBase = ref(null)
const edicaoPrefixo = ref('')
const salvandoEdicao = ref(false)

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
  const basesEscolhidas = baseFiltro.value || []

  return equipes.value.filter(equipe => {
    if (basesEscolhidas.length && !basesEscolhidas.includes(equipe.base)) {
      return false
    }

    if (
      tipoFiltro.value !== TIPO_TODOS &&
      ehEquipeFolguista(equipe) !== (tipoFiltro.value === 'FOLGUISTA')
    ) {
      return false
    }

    return (
      !termo || `${equipe.prefixo} ${equipe.base}`.toLowerCase().includes(termo)
    )
  })
})

const podeAplicarPlanilha = computed(() => {
  const plano = planoPlanilha.value
  if (!plano || plano.erros.length) {
    return false
  }
  return Boolean(plano.criar.length || plano.editar.length || plano.excluir.length)
})

const podeSalvarEdicao = computed(() =>
  Boolean((edicaoBase.value || '').trim() && edicaoPrefixo.value.trim())
)

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

async function baixarPlanilha() {
  erro.value = ''
  baixandoPlanilha.value = true

  try {
    const resposta = await fetch('/api/equipes/planilha')

    if (!resposta.ok) {
      const dados = await resposta.json().catch(() => ({}))
      throw new Error(dados.erro || 'Erro ao gerar a planilha.')
    }

    const blob = await resposta.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'equipes.xlsx'
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    erro.value = e.message || 'Erro ao gerar a planilha.'
  } finally {
    baixandoPlanilha.value = false
  }
}

async function enviarPlanilha(rota) {
  const corpo = new FormData()
  corpo.append('arquivo', arquivoPlanilha.value)

  const resposta = await fetch(rota, { method: 'POST', body: corpo })
  const dados = await resposta.json()

  return { ok: resposta.ok, dados }
}

async function analisarPlanilha() {
  if (!arquivoPlanilha.value) {
    return
  }

  erro.value = ''
  sucesso.value = ''
  analisandoPlanilha.value = true

  try {
    const { ok, dados } = await enviarPlanilha('/api/equipes/planilha/previa')

    if (!ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao analisar a planilha.')
    }

    planoPlanilha.value = dados
    dialogPlanilha.value = true
  } catch (e) {
    erro.value = e.message || 'Erro ao analisar a planilha.'
  } finally {
    analisandoPlanilha.value = false
  }
}

async function aplicarPlanilha() {
  erro.value = ''
  sucesso.value = ''
  aplicandoPlanilha.value = true

  try {
    const { ok, dados } = await enviarPlanilha('/api/equipes/planilha/aplicar')

    if (!ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao aplicar a planilha.')
    }

    sucesso.value =
      `Planilha aplicada: ${dados.criadas} equipe(s) criada(s), ` +
      `${dados.editadas} editada(s), ${dados.excluidas} excluída(s).`

    dialogPlanilha.value = false
    planoPlanilha.value = null
    arquivoPlanilha.value = null

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao aplicar a planilha.'
  } finally {
    aplicandoPlanilha.value = false
  }
}

function abrirEdicaoEquipe(equipe) {
  equipeEmEdicao.value = equipe
  edicaoBase.value = equipe.base
  edicaoPrefixo.value = equipe.prefixo
  dialogEdicao.value = true
}

async function salvarEdicaoEquipe() {
  erro.value = ''
  sucesso.value = ''
  salvandoEdicao.value = true

  try {
    const resposta = await fetch(`/api/equipes/${equipeEmEdicao.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        base: edicaoBase.value,
        prefixo: edicaoPrefixo.value
      })
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao atualizar a equipe.')
    }

    sucesso.value = `Equipe ${dados.equipe.prefixo} atualizada com sucesso.`
    dialogEdicao.value = false

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao atualizar a equipe.'
  } finally {
    salvandoEdicao.value = false
  }
}

async function liberarEquipe(equipe) {
  const ocupadas = (equipe.vagas || []).filter(vaga => vaga.ocupada)

  if (!ocupadas.length) {
    return
  }

  if (
    !window.confirm(
      `Remover os ${ocupadas.length} colaboradores da equipe ${equipe.prefixo}?`
    )
  ) {
    return
  }

  erro.value = ''
  sucesso.value = ''

  try {
    const resposta = await fetch(`/api/equipes/${equipe.id}/membros`, {
      method: 'DELETE'
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao remover os colaboradores da equipe.')
    }

    sucesso.value = dados.mensagem

    await carregarEquipes()
  } catch (e) {
    erro.value = e.message || 'Erro ao remover os colaboradores da equipe.'
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

onMounted(carregarEquipes)
</script>
