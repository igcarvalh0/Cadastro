<template>
  <q-layout view="lHh Lpr lFf">
    <CabecalhoApp
      titulo="Banco de Dados"
      :carregando="carregando"
      @atualizar="carregarDados"
    />

    <q-page-container>
      <q-page class="q-pa-md banco-page">
        <!-- ================================================== -->
        <!-- CABEÇALHO -->
        <!-- ================================================== -->

        <div class="q-mb-md">
          <div class="text-h5"> Banco de Dados </div>

          <div class="text-subtitle2 text-grey-7">
            Gerenciamento de equipes e colaboradores
          </div>
        </div>

        <!-- ================================================== -->
        <!-- STATUS -->
        <!-- ================================================== -->

        <q-banner v-if="erro" class="bg-red-1 text-negative q-mb-md" rounded>
          {{ erro }}
        </q-banner>

        <!-- ================================================== -->
        <!-- FILTROS -->
        <!-- ================================================== -->

        <q-card flat bordered class="q-mb-md">
          <q-card-section>
            <div class="row items-center q-col-gutter-md">
              <div class="col-12 col-md-4">
                <q-select
                  :model-value="baseSelecionada"
                  :options="opcoesBases"
                  label="Base"
                  outlined
                  dense
                  clearable
                  multiple
                  use-chips
                  emit-value
                  map-options
                  @update:model-value="atualizarSelecaoBases"
                />
              </div>

              <div class="col-12 col-md-3">
                <q-select
                  v-model="tipoSelecionado"
                  :options="OPCOES_TIPO"
                  label="Tipo"
                  outlined
                  dense
                  emit-value
                  map-options
                />
              </div>

              <div class="col-auto">
                <q-chip color="primary" text-color="white">
                  {{ equipesFiltradas.length }} equipes
                </q-chip>
              </div>

              <div class="col-auto">
                <q-chip color="positive" text-color="white">
                  {{ colaboradoresAlocados }} alocados
                </q-chip>
              </div>

              <div class="col-auto">
                <q-chip color="grey-7" text-color="white">
                  {{ colaboradoresLivres }} livres
                </q-chip>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- ================================================== -->
        <!-- CONTEÚDO -->
        <!-- ================================================== -->

        <div v-if="carregando" class="row justify-center q-pa-xl">
          <q-spinner color="primary" size="50px" />
        </div>

        <div v-else class="row q-col-gutter-md">
          <!-- ================================================= -->
          <!-- EQUIPES -->
          <!-- ================================================= -->

          <div class="col-12 col-lg-8">
            <q-card bordered>
              <q-card-section class="text-center">
                <div class="text-h6"> Equipes </div>
              </q-card-section>

              <q-separator />

              <q-list separator>
                <q-expansion-item
                  v-for="equipe in equipesFiltradas"
                  :key="equipe.id"
                  expand-separator
                  :label="equipe.prefixo || 'Equipe'"
                  :caption="equipe.base || ''"
                  header-class="equipe-header"
                  expand-icon="fiber_manual_record"
                  expanded-icon="fiber_manual_record"
                  :expand-icon-class="
                    equipePreenchida(equipe) ? 'text-positive' : 'text-negative'
                  "
                >
                  <q-card flat>
                    <q-card-section class="q-pb-none text-right">
                      <q-btn
                        outline
                        dense
                        size="sm"
                        color="negative"
                        icon="person_remove"
                        label="Remover todos os colaboradores"
                        :disable="!equipe.vagas.some(vaga => vaga.colaborador)"
                        @click="liberarEquipe(equipe)"
                      >
                        <q-tooltip
                          v-if="!equipe.vagas.some(vaga => vaga.colaborador)"
                        >
                          Nenhum colaborador alocado nesta equipe
                        </q-tooltip>
                      </q-btn>
                    </q-card-section>

                    <q-card-section>
                      <div
                        class="row items-center text-center text-caption text-grey-7 text-weight-medium q-pb-sm"
                      >
                        <div class="col-12 col-sm-2">CHAPA</div>
                        <div class="col-12 col-sm-3">Colaborador</div>
                        <div class="col-12 col-sm-2">Função cadastrada</div>
                        <div class="col-12 col-sm-2">Vaga</div>
                        <div class="col-12 col-sm-3">Status</div>
                      </div>

                      <div v-if="!equipe.vagas.length" class="text-grey-7">
                        Nenhuma vaga cadastrada.
                      </div>

                      <div
                        v-for="vaga in equipe.vagas"
                        :key="vaga.id"
                        class="row items-center text-center q-py-sm"
                      >
                        <div class="col-12 col-sm-2 text-caption">
                          {{ vaga.colaborador?.chapa || '-' }}
                        </div>

                        <div class="col-12 col-sm-3">
                          {{ vaga.colaborador?.nome || 'Vaga livre' }}
                        </div>

                        <div class="col-12 col-sm-2 text-caption">
                          {{ vaga.colaborador?.funcao || '-' }}
                        </div>

                        <div class="col-12 col-sm-2 text-weight-medium">
                          {{ vaga.funcao_er || 'Não informada' }}
                        </div>

                        <div
                          class="col-12 col-sm-3 flex justify-center items-center"
                        >
                          <q-chip
                            v-if="vaga.colaborador"
                            color="positive"
                            text-color="white"
                            size="sm"
                          >
                            ALOCADO
                          </q-chip>

                          <q-chip
                            v-else
                            color="grey-5"
                            text-color="white"
                            size="sm"
                          >
                            LIVRE
                          </q-chip>

                          <q-btn
                            v-if="vaga.colaborador"
                            flat
                            round
                            dense
                            color="negative"
                            icon="person_remove"
                            class="q-ml-sm"
                            aria-label="Remover colaborador"
                            @click="removerColaborador(vaga.id)"
                          />

                          <q-btn
                            v-else
                            flat
                            round
                            dense
                            color="primary"
                            icon="person_add"
                            class="q-ml-sm"
                            aria-label="Alocar colaborador"
                            @click="abrirAlocacaoParaVaga(equipe, vaga)"
                          />
                        </div>
                      </div>
                    </q-card-section>
                  </q-card>
                </q-expansion-item>
              </q-list>
            </q-card>
          </div>

          <!-- ================================================= -->
          <!-- COLABORADORES -->
          <!-- ================================================= -->

          <div class="col-12 col-lg-4">
            <q-card bordered>
              <q-card-section class="text-center">
                <div class="text-h6"> Colaboradores </div>
              </q-card-section>

              <q-separator />

              <q-card-section>
                <div class="row q-col-gutter-sm q-mb-md">
                  <div class="col">
                    <q-input
                      v-model="filtroColaborador"
                      outlined
                      dense
                      clearable
                      placeholder="Pesquisar por nome ou chapa..."
                    >
                      <template #prepend>
                        <q-icon name="search" />
                      </template>
                    </q-input>
                  </div>

                  <div class="col-auto">
                    <q-btn
                      :color="
                        statusColaborador === 'TODOS' ? 'primary' : 'grey-7'
                      "
                      outline
                      label="Todos"
                      @click="statusColaborador = 'TODOS'"
                    />
                  </div>

                  <div class="col-auto">
                    <q-btn
                      :color="
                        statusColaborador === 'ALOCADOS' ? 'positive' : 'grey-7'
                      "
                      outline
                      :label="`Alocados (${colaboradoresAlocados})`"
                      @click="statusColaborador = 'ALOCADOS'"
                    />
                  </div>

                  <div class="col-auto">
                    <q-btn
                      :color="
                        statusColaborador === 'LIVRES' ? 'primary' : 'grey-7'
                      "
                      outline
                      :label="`Livres (${colaboradoresLivres})`"
                      @click="statusColaborador = 'LIVRES'"
                    />
                  </div>
                </div>

                <q-list bordered separator class="rounded-borders">
                  <q-item
                    v-for="colaborador in colaboradoresFiltrados"
                    :key="colaborador.chapa"
                    clickable
                    :disable="colaborador.alocado"
                    @click="selecionarColaborador(colaborador)"
                  >
                    <q-item-section class="text-center">
                      <q-item-label>
                        {{ colaborador.nome }}
                      </q-item-label>

                      <q-item-label caption>
                        {{ colaborador.funcao }}
                      </q-item-label>

                      <q-item-label caption>
                        SEÇÃO: {{ colaborador.secao || 'Não informada' }}
                      </q-item-label>
                    </q-item-section>

                    <q-item-section side class="text-center">
                      <q-chip
                        v-if="colaborador.alocado"
                        color="positive"
                        text-color="white"
                        size="sm"
                      >
                        ALOCADO
                      </q-chip>

                      <q-chip
                        v-else
                        color="grey-6"
                        text-color="white"
                        size="sm"
                      >
                        LIVRE
                      </q-chip>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-card-section>
            </q-card>
          </div>
        </div>
      </q-page>
    </q-page-container>

    <q-dialog v-model="dialogAlocacao">
      <q-card style="min-width: 500px; max-width: 90vw">
        <q-card-section>
          <div class="text-h6"> Alocar colaborador </div>

          <div
            v-if="colaboradorSelecionado"
            class="text-subtitle2 text-grey-7 q-mt-sm"
          >
            {{ colaboradorSelecionado.chapa }}
            -
            {{ colaboradorSelecionado.nome }}
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <q-select
            v-model="colaboradorSelecionado"
            :options="colaboradoresLivresAlocacao"
            label="Colaborador"
            outlined
            dense
            use-input
            clearable
            option-label="nome"
            input-debounce="0"
            class="q-mb-md"
            hint="Pesquise pelo nome ou pela CHAPA"
            @filter="filtrarColaboradoresAlocacao"
          >
            <template #option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.nome }}</q-item-label>
                  <q-item-label caption>
                    CHAPA: {{ scope.opt.chapa }} |
                    {{ scope.opt.funcao || 'Função não informada' }}
                  </q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>

          <q-select
            v-model="baseAlocacao"
            :options="basesAlocacao"
            label="Base"
            outlined
            dense
            emit-value
            map-options
            clearable
            @update:model-value="limparEquipeAlocacao"
          />

          <q-select
            v-if="baseAlocacao"
            v-model="equipeAlocacao"
            :options="equipesAlocacao"
            label="Equipe"
            outlined
            dense
            emit-value
            map-options
            clearable
            class="q-mt-md"
            @update:model-value="limparVagaAlocacao"
          />

          <q-select
            v-if="equipeAlocacao"
            v-model="vagaAlocacao"
            :options="vagasAlocacao"
            label="Vaga"
            outlined
            dense
            emit-value
            map-options
            clearable
            class="q-mt-md"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup />

          <q-btn
            color="primary"
            label="Alocar"
            :loading="carregandoAlocacao"
            :disable="!vagaAlocacao"
            @click="alocarColaborador"
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

// ============================================================
// ESTADO
// ============================================================

const equipes = ref([])

const colaboradores = ref([])

const carregando = ref(false)

const erro = ref('')

const baseSelecionada = ref([])
const tipoSelecionado = ref(TIPO_TODOS)

const filtroColaborador = ref('')
const statusColaborador = ref('TODOS')
const colaboradoresLivresAlocacao = ref([])

const opcoesAlocacao = ref({})
const colaboradorSelecionado = ref(null)
const dialogAlocacao = ref(false)
const carregandoAlocacao = ref(false)

const baseAlocacao = ref(null)
const equipeAlocacao = ref(null)
const vagaAlocacao = ref(null)

const basesAlocacao = computed(() => {
  return Object.keys(opcoesAlocacao.value)
    .sort((a, b) => a.localeCompare(b, 'pt-BR'))
    .map(base => ({
      label: base,
      value: base
    }))
})

const equipesAlocacao = computed(() => {
  if (!baseAlocacao.value) {
    return []
  }

  return (opcoesAlocacao.value[baseAlocacao.value] || [])
    .map(equipe => ({
      label: equipe.prefixo || 'Equipe sem prefixo',
      value: equipe.id
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'pt-BR'))
})

const vagasAlocacao = computed(() => {
  if (!baseAlocacao.value || !equipeAlocacao.value) {
    return []
  }

  const equipe = (opcoesAlocacao.value[baseAlocacao.value] || []).find(
    item => String(item.id) === String(equipeAlocacao.value)
  )

  if (!equipe) {
    return []
  }

  return (equipe.vagas || []).map(vaga => ({
    label:
      [vaga.funcao_er, vaga.estrutura].filter(Boolean).join(' | ') ||
      'Função não informada',
    value: vaga.id
  }))
})

// ============================================================
// BASES
// ============================================================

const OPCAO_TODAS_BASES = '__TODAS_BASES__'

const CODIGOS_BASES = {
  BACABAL: 'BCB',
  ITAPECURU: 'ITM',
  'ITAPECURU MIRIM': 'ITM',
  'SANTA INES': 'STI',
  'SPOT STI': 'SPOT STI',
  PEDREIRAS: 'PDS',
  'PRES DUTRA': 'PDT',
  'PRESIDENTE DUTRA': 'PDT',
  'BARRA DO CORDA': 'BDC'
}

function normalizarSelecaoBases(bases) {
  if (!Array.isArray(bases)) {
    return []
  }

  const valores = [...new Set(bases.filter(Boolean))]

  if (valores.includes(OPCAO_TODAS_BASES)) {
    return [OPCAO_TODAS_BASES]
  }

  return valores
}

function equipePreenchida(equipe) {
  const vagas = equipe.vagas || []

  return vagas.length > 0 && vagas.every(vaga => Boolean(vaga.colaborador))
}

function atualizarSelecaoBases(bases) {
  const selecao = Array.isArray(bases) ? bases : []

  if (
    selecao.includes(OPCAO_TODAS_BASES) &&
    baseSelecionada.value.includes(OPCAO_TODAS_BASES) &&
    selecao.length > 1
  ) {
    baseSelecionada.value = selecao.filter(base => base !== OPCAO_TODAS_BASES)
    return
  }

  baseSelecionada.value = normalizarSelecaoBases(selecao)
}

const opcoesBases = computed(() => {
  const bases = [
    {
      label: 'Todas as bases',
      value: OPCAO_TODAS_BASES
    }
  ]

  for (const equipe of equipes.value) {
    const base = String(equipe.base || '').trim()

    if (!base) {
      continue
    }

    if (!bases.some(item => item.value === base)) {
      const codigo = CODIGOS_BASES[base]
      bases.push({
        label: codigo ? `${base} (${codigo})` : base,
        value: base
      })
    }
  }

  return bases.sort((a, b) => {
    if (a.value === OPCAO_TODAS_BASES) return -1
    if (b.value === OPCAO_TODAS_BASES) return 1
    return a.label.localeCompare(b.label, 'pt-BR')
  })
})

// ============================================================
// EQUIPES FILTRADAS
// ============================================================

const equipesFiltradas = computed(() => {
  const visiveisPorBase =
    !baseSelecionada.value.length ||
    baseSelecionada.value.includes(OPCAO_TODAS_BASES)
      ? equipes.value
      : equipes.value.filter(equipe => {
          const base = String(equipe.base || '').trim()
          return baseSelecionada.value.includes(base)
        })

  const equipesVisiveis =
    tipoSelecionado.value === TIPO_TODOS
      ? visiveisPorBase
      : visiveisPorBase.filter(
          equipe =>
            ehEquipeFolguista(equipe) === (tipoSelecionado.value === 'FOLGUISTA')
        )

  return [...equipesVisiveis].sort((a, b) => {
    const baseA = String(a.base || '').trim()
    const baseB = String(b.base || '').trim()
    const comparacaoBase = baseA.localeCompare(baseB, 'pt-BR')

    if (comparacaoBase !== 0) {
      return comparacaoBase
    }

    const prefixoA = String(a.prefixo || '').trim()
    const prefixoB = String(b.prefixo || '').trim()
    const tipoA = prefixoA.toUpperCase() === 'FOLGUISTA' ? 1 : 0
    const tipoB = prefixoB.toUpperCase() === 'FOLGUISTA' ? 1 : 0

    if (tipoA !== tipoB) {
      return tipoA - tipoB
    }

    return prefixoA.localeCompare(prefixoB, 'pt-BR')
  })
})

// ============================================================
// COLABORADORES FILTRADOS
// ============================================================

const colaboradoresBase = computed(() => {
  if (
    !baseSelecionada.value.length ||
    baseSelecionada.value.includes(OPCAO_TODAS_BASES)
  ) {
    return colaboradores.value
  }

  return colaboradores.value.filter(colaborador =>
    baseSelecionada.value.some(
      base =>
        base === colaborador.base ||
        CODIGOS_BASES[base] === colaborador.codigo_base
    )
  )
})

const colaboradoresFiltrados = computed(() => {
  const filtro = filtroColaborador.value.trim().toLowerCase()

  return colaboradoresBase.value.filter(colaborador => {
    const correspondeStatus =
      statusColaborador.value === 'TODOS' ||
      (statusColaborador.value === 'ALOCADOS' && colaborador.alocado) ||
      (statusColaborador.value === 'LIVRES' && !colaborador.alocado)

    const correspondeTexto =
      !filtro ||
      String(colaborador.nome || '')
        .toLowerCase()
        .includes(filtro) ||
      String(colaborador.chapa || '')
        .toLowerCase()
        .includes(filtro) ||
      String(colaborador.funcao || '')
        .toLowerCase()
        .includes(filtro)

    return correspondeStatus && correspondeTexto
  })
})

// ============================================================
// CONTADORES
// ============================================================

const colaboradoresAlocados = computed(() => {
  return colaboradoresBase.value.filter(colaborador => colaborador.alocado)
    .length
})

const colaboradoresLivres = computed(() => {
  return colaboradoresBase.value.filter(colaborador => !colaborador.alocado)
    .length
})

// ============================================================
// CARREGAR DADOS
// ============================================================

async function carregarDados() {
  carregando.value = true

  erro.value = ''

  try {
    const [respostaEquipes, respostaColaboradores] = await Promise.all([
      fetch('/api/equipes'),

      fetch('/api/colaboradores')
    ])

    if (!respostaEquipes.ok) {
      throw new Error('Erro ao carregar equipes.')
    }

    if (!respostaColaboradores.ok) {
      throw new Error('Erro ao carregar colaboradores.')
    }

    const dadosEquipes = await respostaEquipes.json()

    const dadosColaboradores = await respostaColaboradores.json()

    if (dadosEquipes.erro) {
      throw new Error(dadosEquipes.erro)
    }

    if (dadosColaboradores.erro) {
      throw new Error(dadosColaboradores.erro)
    }

    equipes.value = dadosEquipes

    colaboradores.value = dadosColaboradores

    const respostaOpcoes = await fetch('/api/opcoes-alocacao')

    if (!respostaOpcoes.ok) {
      throw new Error('Erro ao carregar opções de alocação.')
    }

    const dadosOpcoes = await respostaOpcoes.json()

    if (dadosOpcoes.erro) {
      throw new Error(dadosOpcoes.erro)
    }

    opcoesAlocacao.value = dadosOpcoes
  } catch (e) {
    console.error(e)

    erro.value = e.message || 'Erro ao carregar dados.'
  } finally {
    carregando.value = false
  }
}

function selecionarColaborador(colaborador) {
  if (colaborador.alocado) {
    return
  }

  colaboradorSelecionado.value = colaborador
  colaboradoresLivresAlocacao.value = colaboradores.value.filter(
    item => !item.alocado
  )

  dialogAlocacao.value = true
}

function abrirAlocacaoParaVaga(equipe, vaga) {
  colaboradorSelecionado.value = null
  baseAlocacao.value = equipe.base
  equipeAlocacao.value = equipe.id
  vagaAlocacao.value = vaga.id
  colaboradoresLivresAlocacao.value = colaboradores.value.filter(
    colaborador => !colaborador.alocado
  )
  dialogAlocacao.value = true
}

function filtrarColaboradoresAlocacao(valor, atualizar) {
  atualizar(() => {
    const filtro = String(valor || '')
      .trim()
      .toLowerCase()

    colaboradoresLivresAlocacao.value = colaboradores.value.filter(
      colaborador => {
        return (
          !colaborador.alocado &&
          (!filtro ||
            String(colaborador.nome || '')
              .toLowerCase()
              .includes(filtro) ||
            String(colaborador.chapa || '')
              .toLowerCase()
              .includes(filtro))
        )
      }
    )
  })
}

function limparEquipeAlocacao() {
  equipeAlocacao.value = null
  vagaAlocacao.value = null
}

function limparVagaAlocacao() {
  vagaAlocacao.value = null
}

function localizarVaga(composicaoId) {
  for (const equipe of equipes.value) {
    const vaga = (equipe.vagas || []).find(
      item => String(item.id) === String(composicaoId)
    )

    if (vaga) {
      return vaga
    }
  }

  return null
}

function atualizarEstadoAposAlocacao(composicaoId, colaborador) {
  const vaga = localizarVaga(composicaoId)

  if (vaga) {
    vaga.colaborador = {
      ...colaborador,
      alocado: true
    }
    vaga.ocupada = true
  }

  const colaboradorLista = colaboradores.value.find(
    item => item.chapa === colaborador.chapa
  )

  if (colaboradorLista) {
    colaboradorLista.alocado = true
  }

  for (const equipe of Object.values(opcoesAlocacao.value)) {
    const equipeAlocacaoAtual = equipe.find(item =>
      (item.vagas || []).some(
        vagaItem => String(vagaItem.id) === String(composicaoId)
      )
    )

    if (equipeAlocacaoAtual) {
      equipeAlocacaoAtual.vagas = equipeAlocacaoAtual.vagas.filter(
        vagaItem => String(vagaItem.id) !== String(composicaoId)
      )
      break
    }
  }
}

function atualizarEstadoAposRemocao(chapa, composicaoId) {
  const vaga = localizarVaga(composicaoId)

  if (vaga) {
    vaga.colaborador = null
    vaga.ocupada = false
  }

  const colaborador = colaboradores.value.find(item => item.chapa === chapa)

  if (colaborador) {
    colaborador.alocado = false
  }
}

async function alocarColaborador() {
  if (!colaboradorSelecionado.value || !vagaAlocacao.value) {
    return
  }

  carregandoAlocacao.value = true
  const composicaoId = vagaAlocacao.value

  try {
    const resposta = await fetch('/api/equipes/alocar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        composicao_id: vagaAlocacao.value,
        chapa: colaboradorSelecionado.value.chapa
      })
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao alocar colaborador.')
    }

    dialogAlocacao.value = false
    colaboradorSelecionado.value = null
    baseAlocacao.value = null
    equipeAlocacao.value = null
    vagaAlocacao.value = null

    atualizarEstadoAposAlocacao(composicaoId, dados.colaborador)
  } catch (e) {
    erro.value = e.message || 'Erro ao alocar colaborador.'
  } finally {
    carregandoAlocacao.value = false
  }
}

async function removerColaborador(composicaoId) {
  if (!window.confirm('Deseja realmente remover este colaborador da equipe?')) {
    return
  }

  erro.value = ''
  const vaga = equipes.value
    .flatMap(equipe => equipe.vagas || [])
    .find(item => String(item.id) === String(composicaoId))
  const chapa = vaga?.colaborador?.chapa

  try {
    const resposta = await fetch('/api/equipes/remover', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        composicao_id: composicaoId
      })
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao remover colaborador.')
    }

    atualizarEstadoAposRemocao(chapa, composicaoId)
  } catch (e) {
    erro.value = e.message || 'Erro ao remover colaborador.'
  }
}

async function liberarEquipe(equipe) {
  const ocupadas = (equipe.vagas || []).filter(vaga => vaga.colaborador)

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

  try {
    const resposta = await fetch(`/api/equipes/${equipe.id}/membros`, {
      method: 'DELETE'
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Erro ao remover os colaboradores da equipe.')
    }

    ocupadas.forEach(vaga => {
      atualizarEstadoAposRemocao(vaga.colaborador?.chapa, vaga.id)
    })
  } catch (e) {
    erro.value = e.message || 'Erro ao remover os colaboradores da equipe.'
  }
}

// ============================================================
// INICIALIZAÇÃO
// ============================================================

onMounted(() => {
  carregarDados().then(() => {
    try {
      const filtroSalvo = JSON.parse(
        localStorage.getItem('gerenciadorEquipes_basesSelecionadas') || '[]'
      )

      if (Array.isArray(filtroSalvo)) {
        if (filtroSalvo.length === 0) {
          baseSelecionada.value = [OPCAO_TODAS_BASES]
        } else {
          const basesExistentes = opcoesBases.value.map(opcao => opcao.value)
          const validas = filtroSalvo.filter(
            base => basesExistentes.includes(base) || base === OPCAO_TODAS_BASES
          )
          baseSelecionada.value = validas.length
            ? normalizarSelecaoBases(validas)
            : [OPCAO_TODAS_BASES]
        }
      } else {
        baseSelecionada.value = [OPCAO_TODAS_BASES]
      }
    } catch {
      baseSelecionada.value = [OPCAO_TODAS_BASES]
    }
  })
})

watch(
  baseSelecionada,
  bases => {
    const basesNormalizadas = normalizarSelecaoBases(bases)

    if (JSON.stringify(basesNormalizadas) !== JSON.stringify(bases)) {
      baseSelecionada.value = basesNormalizadas
      return
    }

    localStorage.setItem(
      'gerenciadorEquipes_basesSelecionadas',
      JSON.stringify(basesNormalizadas)
    )
  },
  { deep: true }
)
</script>

<style scoped>
.banco-page :deep(.q-list .q-item__section--main) {
  text-align: center;
}

.banco-page :deep(.equipe-header .q-item__section--main) {
  align-items: flex-start !important;
  justify-content: flex-start !important;
  text-align: left !important;
  width: 100%;
}

.banco-page :deep(.equipe-header .q-item__label) {
  display: block;
  width: 100%;
  text-align: left !important;
}
</style>
