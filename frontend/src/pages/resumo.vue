<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="site-header text-white">
      <q-toolbar>
        <q-btn flat round dense icon="arrow_back" @click="voltar" />

        <div class="site-logo q-mr-sm">
          <img src="/icons/favicon-128x128.png" alt="Logo" />
        </div>

        <q-toolbar-title> Resumo </q-toolbar-title>

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
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="q-pa-sm resumo-page">
        <!-- ================================================== -->
        <!-- CABEÇALHO -->
        <!-- ================================================== -->

        <div class="row items-center q-mb-md">
          <div class="col">
            <div class="text-h5"> Resumo </div>

            <div class="text-subtitle2 text-grey-7">
              Resumo das equipes e colaboradores
            </div>
          </div>

          <div class="col-auto">
            <q-btn
              color="primary"
              icon="refresh"
              label="Atualizar"
              :loading="carregando"
              @click="carregarResumo"
            />
          </div>
        </div>

        <!-- ================================================== -->
        <!-- ERRO -->
        <!-- ================================================== -->

        <q-banner v-if="erro" class="bg-red-1 text-negative q-mb-md" rounded>
          {{ erro }}
        </q-banner>

        <!-- ================================================== -->
        <!-- FILTRO DE BASE -->
        <!-- ================================================== -->

        <q-card flat bordered class="q-mb-md">
          <q-card-section>
            <div class="row items-center q-col-gutter-md">
              <div class="col-12 col-md-4">
                <q-select
                  v-model="baseSelecionada"
                  :options="opcoesBases"
                  label="Base"
                  outlined
                  dense
                  clearable
                  multiple
                  use-chips
                  emit-value
                  map-options
                />
              </div>

              <div class="col-auto">
                <q-chip color="primary" text-color="white">
                  {{ totalExibido.equipes.CONSTRUÇÃO }} construção
                </q-chip>
              </div>

              <div class="col-auto">
                <q-chip color="orange" text-color="white">
                  {{ totalExibido.equipes.FOLGUISTA }} folguistas
                </q-chip>
              </div>

              <div class="col-auto">
                <q-chip color="positive" text-color="white">
                  {{ totalExibido.alocados }} alocados
                </q-chip>
              </div>

              <div class="col-auto">
                <q-chip color="grey-7" text-color="white">
                  {{ totalExibido.vagas }} vagas
                </q-chip>
              </div>
            </div>
          </q-card-section>
        </q-card>

        <!-- ================================================== -->
        <!-- CARREGANDO -->
        <!-- ================================================== -->

        <div v-if="carregando" class="row justify-center q-pa-xl">
          <q-spinner color="primary" size="50px" />
        </div>

        <!-- ================================================== -->
        <!-- RESUMO -->
        <!-- ================================================== -->

        <div v-else class="row q-col-gutter-md">
          <!-- ================================================= -->
          <!-- BASES -->
          <!-- ================================================= -->

          <div class="col-12 resumo-composicao">
            <div class="text-overline text-primary text-weight-bold q-mb-sm">
              Composição das equipes
            </div>

            <q-card
              v-for="base in basesExibidas"
              :key="base.codigo"
              bordered
              class="q-mb-md"
            >
              <!-- =============================================== -->
              <!-- CABEÇALHO DA BASE -->
              <!-- =============================================== -->

              <q-card-section>
                <div class="row items-center">
                  <div class="col">
                    <div class="text-h6">
                      {{ base.base }}
                    </div>

                    <div class="text-caption text-grey-7">
                      Código: {{ base.codigo }}
                    </div>
                  </div>

                  <div class="col-auto">
                    <div class="row q-gutter-sm">
                      <q-chip color="primary" text-color="white">
                        {{ base.equipes.CONSTRUÇÃO }}
                        construção
                      </q-chip>

                      <q-chip color="orange" text-color="white">
                        {{ base.equipes.FOLGUISTA }}
                        folguistas
                      </q-chip>
                    </div>
                  </div>
                </div>
              </q-card-section>

              <q-separator />

              <!-- =============================================== -->
              <!-- TABELA -->
              <!-- =============================================== -->

              <q-card-section>
                <q-table
                  flat
                  bordered
                  dense
                  class="tabela-equipe"
                  :rows="base.funcoes"
                  :columns="colunas"
                  row-key="funcao"
                  hide-pagination
                  :rows-per-page-options="[0]"
                >
                  <!-- =========================================== -->
                  <!-- EQUIPE -->
                  <!-- =========================================== -->

                  <template #body-cell-equipe="props">
                    <q-td :props="props">
                      <q-chip
                        v-if="props.row.equipe === 'CONSTRUÇÃO'"
                        color="primary"
                        text-color="white"
                        size="sm"
                      >
                        CONSTRUÇÃO
                      </q-chip>

                      <q-chip
                        v-else
                        color="orange"
                        text-color="white"
                        size="sm"
                      >
                        FOLGUISTA
                      </q-chip>
                    </q-td>
                  </template>

                  <!-- =========================================== -->
                  <!-- FUNÇÃO -->
                  <!-- =========================================== -->

                  <template #body-cell-funcao="props">
                    <q-td :props="props">
                      <span class="text-weight-medium">
                        {{ props.row.funcao }}
                      </span>
                    </q-td>
                  </template>

                  <!-- =========================================== -->
                  <!-- DIFERENÇA -->
                  <!-- =========================================== -->

                  <template #body-cell-diferenca="props">
                    <q-td :props="props">
                      <q-chip
                        :color="
                          props.row.diferenca < 0
                            ? 'negative'
                            : props.row.diferenca > 0
                              ? 'positive'
                              : 'grey-6'
                        "
                        text-color="white"
                        size="sm"
                      >
                        {{ props.row.diferenca }}
                      </q-chip>
                    </q-td>
                  </template>
                </q-table>
              </q-card-section>
            </q-card>
          </div>

          <!-- ================================================= -->
          <!-- TOTAL GERAL -->
          <!-- ================================================= -->

          <div class="col-12 resumo-lateral">
            <div class="text-overline text-primary text-weight-bold q-mb-sm">
              Indicadores gerais
            </div>

            <q-card bordered>
              <q-card-section>
                <div class="text-h6 q-mb-md">Total geral</div>

                <div class="row q-col-gutter-md">
                  <div
                    v-for="indicador in indicadoresFuncoes"
                    :key="indicador.funcao"
                    class="col-12 col-sm-6"
                  >
                    <q-card
                      flat
                      bordered
                      class="cursor-pointer"
                      :class="
                        indicador.diferenca < 0 ? 'bg-red-1' : 'bg-green-1'
                      "
                      @click="
                        abrirNecessidades(
                          indicador.funcao,
                          '',
                          indicador.diferenca < 0 ? 'deficit' : 'superavit'
                        )
                      "
                    >
                      <q-card-section>
                        <div class="text-caption text-grey-8">
                          {{ indicador.funcao }}
                        </div>

                        <div
                          class="text-h6"
                          :class="
                            indicador.diferenca < 0
                              ? 'text-negative'
                              : 'text-positive'
                          "
                        >
                          {{
                            indicador.diferenca < 0 ? 'Déficit' : 'Superávit'
                          }}:
                          {{ Math.abs(indicador.diferenca) }}
                        </div>
                      </q-card-section>
                    </q-card>
                  </div>
                </div>

                <!-- ============================================= -->
                <!-- DIFERENÇA TOTAL -->
                <!-- ============================================= -->

                <div class="row justify-center q-mt-lg">
                  <q-chip
                    :color="
                      totalExibido.diferenca < 0
                        ? 'negative'
                        : totalExibido.diferenca > 0
                          ? 'positive'
                          : 'grey-6'
                    "
                    text-color="white"
                    size="lg"
                  >
                    DIFERENÇA TOTAL:
                    {{ totalExibido.diferenca }}
                  </q-chip>
                </div>
              </q-card-section>
            </q-card>

            <q-card bordered class="q-mt-lg">
              <q-card-section>
                <div class="text-h6 q-mb-md">Pessoas alocadas</div>

                <q-table
                  flat
                  bordered
                  :rows="linhasDisponiveis"
                  :columns="colunasDisponiveis"
                  row-key="funcao"
                  hide-pagination
                  :rows-per-page-options="[0]"
                >
                  <template #body="props">
                    <q-tr :props="props">
                      <q-td key="funcao" :props="props">
                        <q-btn
                          flat
                          dense
                          color="primary"
                          class="text-weight-medium"
                          :label="props.row.funcao"
                          @click="abrirDetalhes(props.row.funcao)"
                        />
                      </q-td>

                      <q-td
                        v-for="base in pessoasDisponiveisFiltradas"
                        :key="base.codigo"
                        :props="props"
                        class="text-center"
                      >
                        <q-btn
                          v-if="props.row[base.codigo]"
                          flat
                          dense
                          color="primary"
                          :label="String(props.row[base.codigo])"
                          @click="abrirDetalhes(props.row.funcao, base.codigo)"
                        />

                        <span v-else>0</span>
                      </q-td>

                      <q-td key="total" :props="props" class="text-center">
                        <q-btn
                          v-if="props.row.total"
                          flat
                          dense
                          color="primary"
                          :label="String(props.row.total)"
                          @click="abrirDetalhes(props.row.funcao)"
                        />

                        <span v-else>0</span>
                      </q-td>
                    </q-tr>
                  </template>
                </q-table>
              </q-card-section>
            </q-card>

            <q-card bordered class="q-mt-lg">
              <q-card-section>
                <div class="text-h6 q-mb-md">Pessoas não alocadas</div>

                <q-table
                  flat
                  bordered
                  :rows="linhasNaoAlocadas"
                  :columns="colunasNaoAlocadas"
                  row-key="funcao"
                  hide-pagination
                  :rows-per-page-options="[0]"
                >
                  <template #body="props">
                    <q-tr :props="props">
                      <q-td key="funcao" :props="props">
                        <q-btn
                          flat
                          dense
                          color="primary"
                          class="text-weight-medium"
                          :label="props.row.funcao"
                          @click="abrirNaoAlocados(props.row.funcao)"
                        />
                      </q-td>

                      <q-td
                        v-for="base in basesExibidas"
                        :key="base.codigo"
                        :props="props"
                        class="text-center"
                      >
                        <q-btn
                          v-if="props.row[base.codigo]"
                          flat
                          dense
                          color="primary"
                          :label="String(props.row[base.codigo])"
                          @click="
                            abrirNaoAlocados(props.row.funcao, base.codigo)
                          "
                        />

                        <span v-else>0</span>
                      </q-td>

                      <q-td key="total" :props="props" class="text-center">
                        <q-btn
                          v-if="props.row.total"
                          flat
                          dense
                          color="primary"
                          :label="String(props.row.total)"
                          @click="abrirNaoAlocados(props.row.funcao)"
                        />

                        <span v-else>0</span>
                      </q-td>
                    </q-tr>
                  </template>
                </q-table>
              </q-card-section>
            </q-card>

            <q-dialog v-model="detalhesAbertos">
              <q-card class="detalhes-disponiveis tabela-alocados">
                <q-card-section class="row items-center q-pb-sm">
                  <div class="text-h6">
                    {{ detalheTitulo }}
                  </div>

                  <q-space />

                  <q-btn
                    color="positive"
                    icon="download"
                    label="Exportar Excel"
                    @click="exportarAlocados"
                  />

                  <q-btn v-close-popup flat round dense icon="close" />
                </q-card-section>

                <q-separator />

                <q-card-section>
                  <q-table
                    flat
                    bordered
                    dense
                    class="tabela-exportavel"
                    :rows="detalhesExibidos"
                    :columns="colunasDetalhes"
                    hide-pagination
                    :rows-per-page-options="[0]"
                    no-data-label="Nenhum colaborador encontrado"
                  />
                </q-card-section>
              </q-card>
            </q-dialog>

            <q-dialog v-model="naoAlocadosAbertos">
              <q-card class="detalhes-disponiveis tabela-nao-alocados">
                <q-card-section class="row items-center q-pb-sm">
                  <div class="text-h6">{{ naoAlocadosTitulo }}</div>

                  <q-space />

                  <q-btn
                    color="positive"
                    icon="download"
                    label="Exportar Excel"
                    @click="exportarNaoAlocados"
                  />

                  <q-btn v-close-popup flat round dense icon="close" />
                </q-card-section>

                <q-separator />

                <q-card-section>
                  <q-table
                    flat
                    bordered
                    dense
                    :rows="naoAlocadosDetalhesExibidos"
                    :columns="colunasNaoAlocadosDetalhes"
                    hide-pagination
                    :rows-per-page-options="[0]"
                    no-data-label="Nenhum colaborador encontrado"
                  />
                </q-card-section>
              </q-card>
            </q-dialog>

            <q-dialog v-model="necessidadesAbertas">
              <q-card class="detalhes-disponiveis tabela-necessidades">
                <q-card-section class="row items-center q-pb-sm">
                  <div class="text-h6">{{ necessidadeTitulo }}</div>

                  <q-space />

                  <q-btn v-close-popup flat round dense icon="close" />
                </q-card-section>

                <q-separator />

                <q-card-section>
                  <q-table
                    flat
                    bordered
                    dense
                    :rows="necessidadesExibidas"
                    :columns="colunasNecessidades"
                    hide-pagination
                    :rows-per-page-options="[0]"
                    no-data-label="Nenhuma necessidade encontrada"
                  />
                </q-card-section>
              </q-card>
            </q-dialog>
          </div>
        </div>
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

// ============================================================
// ESTADO
// ============================================================

const bases = ref([])

const total = ref({
  equipes: {
    CONSTRUÇÃO: 0,

    FOLGUISTA: 0
  },

  vagas: 0,

  alocados: 0,

  diferenca: 0
})

const basesFiltro = ref([])

const baseSelecionada = ref([])

const carregando = ref(false)

const erro = ref('')

const pessoasDisponiveis = ref([])

const pessoasNaoAlocadas = ref([])

const naoAlocadosAbertos = ref(false)

const naoAlocadosSelecionados = ref({
  funcao: '',
  codigo: ''
})

const detalhesAbertos = ref(false)

const detalheSelecionado = ref({
  funcao: '',
  codigo: ''
})

const necessidadesAbertas = ref(false)

const necessidadeSelecionada = ref({
  funcao: '',
  codigo: '',
  tipo: 'deficit'
})

// ============================================================
// COLUNAS
// ============================================================

const colunas = [
  {
    name: 'equipe',

    label: 'EQUIPE',

    field: 'equipe',

    align: 'left'
  },

  {
    name: 'funcao',

    label: 'FUNÇÃO',

    field: 'funcao',

    align: 'left'
  },

  {
    name: 'vagas',

    label: 'VAGAS',

    field: 'vagas',

    align: 'center'
  },

  {
    name: 'alocados',

    label: 'ALOCADOS',

    field: 'alocados',

    align: 'center'
  },

  {
    name: 'diferenca',

    label: 'DIFERENÇA',

    field: 'diferenca',

    align: 'center'
  }
]

// ============================================================
// OPÇÕES DE BASE
// ============================================================

const opcoesBases = computed(() => {
  return basesFiltro.value.map(item => ({
    label: `${item.base} (${item.codigo})`,

    value: item.base
  }))
})

const basesExibidas = computed(() => {
  if (
    !baseSelecionada.value.length ||
    baseSelecionada.value.includes('__TODAS_BASES__')
  ) {
    return bases.value
  }

  return bases.value.filter(base => baseSelecionada.value.includes(base.base))
})

const totalExibido = computed(() => {
  return basesExibidas.value.reduce(
    (acumulado, base) => {
      acumulado.equipes['CONSTRUÇÃO'] += base.equipes?.['CONSTRUÇÃO'] || 0
      acumulado.equipes.FOLGUISTA += base.equipes?.FOLGUISTA || 0

      for (const funcao of base.funcoes || []) {
        acumulado.vagas += funcao.vagas || 0
        acumulado.alocados += funcao.alocados || 0
      }

      acumulado.diferenca = acumulado.alocados - acumulado.vagas
      return acumulado
    },
    {
      equipes: {
        CONSTRUÇÃO: 0,
        FOLGUISTA: 0
      },
      vagas: 0,
      alocados: 0,
      diferenca: 0
    }
  )
})

const funcoesDisponiveis = [
  'ENCARREGADO',
  'ELETRICISTA',
  'MOTORISTA',
  'AUXILIAR DE ELETRICISTA'
]

function funcaoResumo(funcao) {
  const valor = String(funcao || '')
    .trim()
    .toUpperCase()

  if (valor === 'ENCARREGADO') {
    return 'ENCARREGADO'
  }

  if (valor === 'ELETRICISTA') {
    return 'ELETRICISTA'
  }

  if (valor === 'MUNQUEIRO/MOTORISTA' || valor === 'MOTORISTA') {
    return 'MOTORISTA'
  }

  if (valor === 'AUXILIAR ELETRICISTA' || valor === 'AUXILIAR DE ELETRICISTA') {
    return 'AUXILIAR DE ELETRICISTA'
  }

  return valor
}

const colunasDisponiveis = computed(() => {
  const colunas = [
    {
      name: 'funcao',
      label: 'FUNÇÃO',
      field: 'funcao',
      align: 'left'
    }
  ]

  for (const base of pessoasDisponiveisFiltradas.value) {
    colunas.push({
      name: base.codigo,
      label: base.codigo,
      field: linha => linha[base.codigo] || 0,
      align: 'center'
    })
  }

  colunas.push({
    name: 'total',
    label: 'TOTAL GERAL',
    field: 'total',
    align: 'center'
  })

  return colunas
})

const colunasNaoAlocadosDetalhes = [
  {
    name: 'chapa',
    label: 'CHAPA',
    field: 'chapa',
    align: 'left'
  },
  {
    name: 'nome',
    label: 'COLABORADOR',
    field: 'nome',
    align: 'left'
  },
  {
    name: 'funcao',
    label: 'FUNÇÃO NO SISTEMA',
    field: 'funcao',
    align: 'left'
  },
  {
    name: 'secao',
    label: 'SEÇÃO',
    field: 'secao',
    align: 'left'
  },
  {
    name: 'codigo',
    label: 'BASE',
    field: 'codigo',
    align: 'center'
  }
]

const colunasNaoAlocadas = computed(() => {
  const colunas = [
    {
      name: 'funcao',
      label: 'FUNÇÃO',
      field: 'funcao',
      align: 'left'
    }
  ]

  for (const base of basesExibidas.value) {
    colunas.push({
      name: base.codigo,
      label: base.codigo,
      field: linha => linha[base.codigo] || 0,
      align: 'center'
    })
  }

  colunas.push({
    name: 'total',
    label: 'TOTAL GERAL',
    field: 'total',
    align: 'center'
  })

  return colunas
})

const colunasDetalhes = [
  {
    name: 'base',
    label: 'BASE',
    field: 'base',
    align: 'left'
  },
  {
    name: 'equipe',
    label: 'EQUIPE',
    field: 'equipe',
    align: 'left'
  },
  {
    name: 'chapa',
    label: 'CHAPA',
    field: 'chapa',
    align: 'left'
  },
  {
    name: 'nome',
    label: 'COLABORADOR',
    field: 'nome',
    align: 'left'
  },
  {
    name: 'funcao_sistema',
    label: 'FUNÇÃO NO SISTEMA',
    field: 'funcao_sistema',
    align: 'left'
  },
  {
    name: 'vaga',
    label: 'VAGA',
    field: 'vaga',
    align: 'left'
  }
]

const colunasNecessidades = [
  {
    name: 'base',
    label: 'BASE',
    field: 'base',
    align: 'left'
  },
  {
    name: 'equipe',
    label: 'EQUIPE',
    field: 'equipe',
    align: 'left'
  },
  {
    name: 'vaga',
    label: 'VAGA',
    field: 'vaga',
    align: 'left'
  },
  {
    name: 'quantidade',
    label: 'QUANTIDADE',
    field: 'quantidade',
    align: 'center'
  }
]

const linhasDisponiveis = computed(() => {
  return funcoesDisponiveis.map(funcao => {
    const linha = { funcao, total: 0 }

    for (const base of pessoasDisponiveisFiltradas.value) {
      const quantidade = base.funcoes?.[funcao] || 0
      linha[base.codigo] = quantidade
      linha.total += quantidade
    }

    return linha
  })
})

const necessidadePorFuncao = computed(() => {
  return basesExibidas.value.reduce((acumulado, base) => {
    for (const linha of base.funcoes || []) {
      if (!acumulado[linha.funcao]) {
        acumulado[linha.funcao] = {
          vagas: 0,
          alocados: 0
        }
      }

      acumulado[linha.funcao].vagas += linha.vagas || 0
      acumulado[linha.funcao].alocados += linha.alocados || 0
    }

    return acumulado
  }, {})
})

const indicadoresFuncoes = computed(() => {
  return funcoesDisponiveis.map(funcao => {
    const necessidade = necessidadePorFuncao.value[funcao] || {
      vagas: 0,
      alocados: 0
    }

    return {
      funcao,
      diferenca: necessidade.alocados - necessidade.vagas
    }
  })
})

const pessoasNaoAlocadasFiltradas = computed(() => {
  const codigosBases = new Set(basesExibidas.value.map(base => base.codigo))

  return pessoasNaoAlocadas.value.filter(pessoa =>
    codigosBases.has(pessoa.codigo)
  )
})

const linhasNaoAlocadas = computed(() => {
  return funcoesDisponiveis.map(funcao => {
    const linha = { funcao, total: 0 }

    for (const base of basesExibidas.value) {
      const quantidade = pessoasNaoAlocadasFiltradas.value.filter(
        pessoa =>
          pessoa.codigo === base.codigo &&
          funcaoResumo(pessoa.funcao) === funcao
      ).length

      linha[base.codigo] = quantidade
      linha.total += quantidade
    }

    return linha
  })
})

const naoAlocadosDetalhesExibidos = computed(() => {
  return pessoasNaoAlocadasFiltradas.value.filter(
    pessoa =>
      funcaoResumo(pessoa.funcao) === naoAlocadosSelecionados.value.funcao &&
      (!naoAlocadosSelecionados.value.codigo ||
        pessoa.codigo === naoAlocadosSelecionados.value.codigo)
  )
})

const naoAlocadosTitulo = computed(() => {
  if (naoAlocadosSelecionados.value.codigo) {
    return `${naoAlocadosSelecionados.value.funcao} em ${naoAlocadosSelecionados.value.codigo}`
  }

  return `${naoAlocadosSelecionados.value.funcao} em todas as bases`
})

const necessidadesExibidas = computed(() => {
  return basesExibidas.value
    .filter(
      base =>
        !necessidadeSelecionada.value.codigo ||
        base.codigo === necessidadeSelecionada.value.codigo
    )
    .flatMap(base =>
      (base.funcoes || [])
        .filter(item => item.funcao === necessidadeSelecionada.value.funcao)
        .map((item, indice) => {
          const diferenca = item.alocados - item.vagas

          return {
            id: `${base.codigo}-${item.equipe}-${indice}`,
            base: base.codigo,
            equipe: item.equipe,
            vaga: item.funcao,
            quantidade:
              necessidadeSelecionada.value.tipo === 'superavit'
                ? Math.max(diferenca, 0)
                : Math.max(-diferenca, 0)
          }
        })
        .filter(item => item.quantidade > 0)
    )
})

const necessidadeTitulo = computed(() => {
  if (necessidadeSelecionada.value.codigo) {
    return `${necessidadeSelecionada.value.funcao} em ${necessidadeSelecionada.value.codigo}`
  }

  const tipo =
    necessidadeSelecionada.value.tipo === 'superavit'
      ? 'Superávit de'
      : 'Déficit de'

  return `${tipo} ${necessidadeSelecionada.value.funcao}`
})

const pessoasDisponiveisFiltradas = computed(() => {
  if (!baseSelecionada.value.length) {
    return pessoasDisponiveis.value
  }

  return pessoasDisponiveis.value.filter(base =>
    baseSelecionada.value.includes(base.base)
  )
})

const detalhesExibidos = computed(() => {
  return pessoasDisponiveisFiltradas.value
    .filter(
      base =>
        !detalheSelecionado.value.codigo ||
        base.codigo === detalheSelecionado.value.codigo
    )
    .flatMap(base => base.detalhes?.[detalheSelecionado.value.funcao] || [])
})

const detalheTitulo = computed(() => {
  if (detalheSelecionado.value.codigo) {
    return `${detalheSelecionado.value.funcao} em ${detalheSelecionado.value.codigo}`
  }

  return `${detalheSelecionado.value.funcao} em todas as bases`
})

function abrirDetalhes(funcao, codigo = '') {
  detalheSelecionado.value = { funcao, codigo }
  detalhesAbertos.value = true
}

function abrirNaoAlocados(funcao, codigo = '') {
  naoAlocadosSelecionados.value = { funcao, codigo }
  naoAlocadosAbertos.value = true
}

function abrirNecessidades(funcao, codigo = '', tipo = 'deficit') {
  necessidadeSelecionada.value = { funcao, codigo, tipo }
  necessidadesAbertas.value = true
}

function escaparCsv(valor) {
  return `"${String(valor ?? '').replaceAll('"', '""')}"`
}

function exportarAlocados() {
  const cabecalho = [
    'BASE',
    'EQUIPE',
    'CHAPA',
    'COLABORADOR',
    'FUNÇÃO NO SISTEMA',
    'VAGA'
  ]

  const linhas = detalhesExibidos.value.map(colaborador => [
    colaborador.base,
    colaborador.equipe,
    colaborador.chapa,
    colaborador.nome,
    colaborador.funcao_sistema,
    colaborador.vaga
  ])

  const csv = [cabecalho, ...linhas]
    .map(linha => linha.map(escaparCsv).join(';'))
    .join('\r\n')
  const arquivo = new Blob([`\ufeff${csv}`], {
    type: 'text/csv;charset=utf-8;'
  })
  const url = URL.createObjectURL(arquivo)
  const link = document.createElement('a')

  link.href = url
  link.download = `pessoas-alocadas-${detalheSelecionado.value.funcao.toLowerCase()}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

function exportarNaoAlocados() {
  const cabecalho = [
    'CHAPA',
    'COLABORADOR',
    'FUNÇÃO NO SISTEMA',
    'SEÇÃO',
    'BASE'
  ]
  const linhas = naoAlocadosDetalhesExibidos.value.map(colaborador => [
    colaborador.chapa,
    colaborador.nome,
    colaborador.funcao,
    colaborador.secao,
    colaborador.base
  ])
  const csv = [cabecalho, ...linhas]
    .map(linha => linha.map(escaparCsv).join(';'))
    .join('\r\n')
  const arquivo = new Blob([`\ufeff${csv}`], {
    type: 'text/csv;charset=utf-8;'
  })
  const url = URL.createObjectURL(arquivo)
  const link = document.createElement('a')

  link.href = url
  link.download = `pessoas-nao-alocadas-${naoAlocadosSelecionados.value.funcao.toLowerCase()}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

// ============================================================
// CARREGAR RESUMO
// ============================================================

async function carregarResumo() {
  carregando.value = true

  erro.value = ''

  try {
    const resposta = await fetch('/api/resumo')

    if (!resposta.ok) {
      throw new Error('Erro ao carregar resumo.')
    }

    const dados = await resposta.json()

    if (dados.erro) {
      throw new Error(dados.erro)
    }

    bases.value = dados.bases || []

    total.value = dados.total || {
      equipes: {
        CONSTRUÇÃO: 0,

        FOLGUISTA: 0
      },

      vagas: 0,

      alocados: 0,

      diferenca: 0
    }

    basesFiltro.value = dados.bases_filtro || []

    pessoasDisponiveis.value = dados.pessoas_disponiveis || []

    pessoasNaoAlocadas.value = dados.pessoas_nao_alocadas || []
  } catch (e) {
    console.error(e)

    erro.value = e.message || 'Erro ao carregar resumo.'
  } finally {
    carregando.value = false
  }
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

// ============================================================
// INICIALIZAÇÃO
// ============================================================

onMounted(() => {
  restaurarModoNoturno()

  carregarResumo().then(() => {
    try {
      const filtroSalvo = JSON.parse(
        localStorage.getItem('gerenciadorEquipes_basesSelecionadas') || '[]'
      )

      if (Array.isArray(filtroSalvo)) {
        const basesExistentes = opcoesBases.value.map(opcao => opcao.value)
        baseSelecionada.value = filtroSalvo.filter(base =>
          basesExistentes.includes(base)
        )
      }
    } catch {
      baseSelecionada.value = []
    }
  })
})

watch(
  baseSelecionada,
  bases => {
    localStorage.setItem(
      'gerenciadorEquipes_basesSelecionadas',
      JSON.stringify(bases.length ? bases : ['__TODAS_BASES__'])
    )
  },
  { deep: true }
)
</script>

<style scoped>
.resumo-page :deep(.q-table thead tr),
.resumo-page :deep(.q-table thead th) {
  background: #711424 !important;
  color: #fff !important;
  font-weight: 700;
  text-align: center !important;
}

.resumo-page {
  font-size: 95%;
}

.resumo-page :deep(.q-card__section) {
  padding: 12px;
}

.resumo-page :deep(.q-table th),
.resumo-page :deep(.q-table td) {
  padding: 3px 5px;
  line-height: 1.15;
}

.resumo-lateral :deep(.q-table th),
.resumo-lateral :deep(.q-table td) {
  padding: 2px 4px !important;
  line-height: 1.1 !important;
}

.resumo-page :deep(.text-h5) {
  font-size: 1.425rem;
}

.resumo-page :deep(.text-h6) {
  font-size: 1.1875rem;
}

.resumo-page :deep(.text-subtitle2) {
  font-size: 0.83125rem;
}

.resumo-composicao,
.resumo-lateral {
  flex: 0 0 100%;
  max-width: 100%;
}

@media (min-width: 1024px) {
  .resumo-composicao {
    flex-basis: 60%;
    max-width: 60%;
  }

  .resumo-lateral {
    flex-basis: 40%;
    max-width: 40%;
  }
}

.tabela-equipe :deep(.q-table th),
.tabela-equipe :deep(.q-table td) {
  padding: 3px 5px;
  line-height: 1.15;
}

.detalhes-disponiveis {
  width: 95vw;
  max-width: 1200px;
}

.tabela-alocados {
  width: 76vw;
  max-width: 960px;
}

.tabela-nao-alocados {
  width: 76vw;
  max-width: 960px;
}

.tabela-exportavel,
.tabela-necessidades,
.tabela-nao-alocados {
  font-size: 90%;
  user-select: text;
}

.tabela-exportavel :deep(th),
.tabela-exportavel :deep(td),
.tabela-necessidades :deep(th),
.tabela-necessidades :deep(td) {
  font-size: 11.9px !important;
  line-height: 1.1 !important;
  padding: 1px 3px !important;
  text-align: center !important;
}

.tabela-nao-alocados :deep(th),
.tabela-nao-alocados :deep(td) {
  font-size: 11.9px !important;
  line-height: 1.1 !important;
  padding: 1px 3px !important;
  text-align: center !important;
}

.tabela-exportavel :deep(table),
.tabela-necessidades :deep(table),
.tabela-nao-alocados :deep(table) {
  white-space: nowrap;
}

.tabela-necessidades {
  width: 53.2vw;
  max-width: 672px;
}

@media (max-width: 600px) {
  .tabela-alocados,
  .tabela-necessidades,
  .tabela-nao-alocados {
    width: 95vw;
  }
}

.tabela-necessidades :deep(th:nth-child(1)),
.tabela-necessidades :deep(td:nth-child(1)) {
  width: 20%;
}

.tabela-necessidades :deep(th:nth-child(2)),
.tabela-necessidades :deep(td:nth-child(2)) {
  width: 30%;
}

.tabela-necessidades :deep(th:nth-child(3)),
.tabela-necessidades :deep(td:nth-child(3)) {
  width: 35%;
}

.tabela-necessidades :deep(th:nth-child(4)),
.tabela-necessidades :deep(td:nth-child(4)) {
  width: 15%;
}
</style>
