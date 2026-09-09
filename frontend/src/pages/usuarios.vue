<template>
  <q-layout view="lHh Lpr lFf">
    <CabecalhoApp
      titulo="Usuários"
      :carregando="carregando"
      @atualizar="carregarTudo"
    />

    <q-page-container>
      <q-page class="q-pa-md">
        <div class="q-mb-md">
          <div class="text-h5"> Usuários </div>

          <div class="text-subtitle2 text-grey-7">
            Quem entra no sistema, o que cada um pode fazer e sobre quais
            equipes
          </div>
        </div>

        <q-banner v-if="erro" class="bg-red-1 text-negative q-mb-md" rounded>
          {{ erro }}
        </q-banner>

        <q-banner v-if="sucesso" class="bg-green-1 text-positive q-mb-md" rounded>
          {{ sucesso }}
        </q-banner>

        <!-- ================================================== -->
        <!-- NÍVEIS DE ACESSO -->
        <!-- ================================================== -->

        <q-card bordered class="q-mb-md">
          <q-card-section>
            <div class="text-h6"> Níveis de acesso </div>

            <div class="text-caption text-grey-7">
              O nível define <strong>o que</strong> a pessoa pode fazer. Os
              vínculos definem <strong>sobre quais equipes</strong>.
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section class="q-pt-sm">
            <q-markup-table flat square dense class="tabela-niveis">
              <thead>
                <tr>
                  <th class="text-left">Nível</th>
                  <th
                    v-for="permissao in PERMISSOES"
                    :key="permissao.valor"
                    class="text-center"
                  >
                    {{ permissao.rotulo }}
                  </th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="nivel in niveis" :key="nivel.valor">
                  <td>
                    <div class="text-weight-medium">{{ nivel.rotulo }}</div>
                    <div class="text-caption text-grey-7">
                      {{ nivel.descricao }}
                    </div>
                  </td>

                  <td
                    v-for="permissao in PERMISSOES"
                    :key="permissao.valor"
                    class="text-center"
                  >
                    <q-icon
                      v-if="nivel.permissoes.includes(permissao.valor)"
                      name="check_circle"
                      color="positive"
                      size="20px"
                    />
                    <q-icon v-else name="remove" color="grey-5" size="18px" />
                  </td>
                </tr>
              </tbody>
            </q-markup-table>

            <q-banner dense class="bg-blue-1 q-mt-md" rounded>
              <template #avatar>
                <q-icon name="info" color="primary" />
              </template>
              Só o nível <strong>Mestre</strong> está definido. Os demais entram
              aqui assim que você disser quais são e o que cada um pode fazer.
            </q-banner>
          </q-card-section>
        </q-card>

        <!-- ================================================== -->
        <!-- LISTA DE USUÁRIOS -->
        <!-- ================================================== -->

        <q-card bordered>
          <q-card-section>
            <div class="row items-center q-col-gutter-sm">
              <div class="col">
                <div class="text-h6"> Cadastrados </div>
              </div>

              <div class="col-auto">
                <q-btn
                  color="primary"
                  icon="person_add"
                  label="Novo usuário"
                  @click="abrirNovo"
                />
              </div>
            </div>
          </q-card-section>

          <q-separator />

          <div v-if="carregando" class="row justify-center q-pa-xl">
            <q-spinner color="primary" size="40px" />
          </div>

          <q-list v-else separator>
            <q-item v-if="!usuarios.length">
              <q-item-section class="text-grey-7">
                Nenhum usuário cadastrado.
              </q-item-section>
            </q-item>

            <q-item v-for="pessoa in usuarios" :key="pessoa.id">
              <q-item-section>
                <q-item-label class="text-weight-medium">
                  {{ pessoa.nome }}
                  <q-badge
                    v-if="pessoa.id === usuario?.id"
                    color="primary"
                    class="q-ml-sm"
                    label="você"
                  />
                  <q-badge
                    v-if="!pessoa.ativo"
                    color="grey-7"
                    class="q-ml-sm"
                    label="desativado"
                  />
                </q-item-label>

                <q-item-label caption>
                  {{ pessoa.usuario }} · {{ pessoa.nivel_rotulo }}
                </q-item-label>

                <q-item-label v-if="resumoVinculos(pessoa)" caption class="q-mt-xs">
                  <q-icon name="link" size="14px" />
                  {{ resumoVinculos(pessoa) }}
                </q-item-label>

                <q-item-label v-else-if="pessoa.ignora_vinculos" caption class="q-mt-xs">
                  <q-icon name="public" size="14px" /> Enxerga todas as equipes
                </q-item-label>
              </q-item-section>

              <q-item-section side>
                <div class="row q-gutter-xs">
                  <q-btn
                    flat
                    dense
                    round
                    icon="edit"
                    color="primary"
                    @click="abrirEdicao(pessoa)"
                  >
                    <q-tooltip>Editar</q-tooltip>
                  </q-btn>

                  <q-btn
                    flat
                    dense
                    round
                    icon="delete"
                    color="negative"
                    :disable="pessoa.id === usuario?.id"
                    @click="removerUsuario(pessoa)"
                  >
                    <q-tooltip>
                      {{
                        pessoa.id === usuario?.id
                          ? 'Você não pode excluir o seu próprio usuário'
                          : 'Excluir'
                      }}
                    </q-tooltip>
                  </q-btn>
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>

        <!-- ================================================== -->
        <!-- FORMULÁRIO -->
        <!-- ================================================== -->

        <q-dialog v-model="dialogAberto">
          <q-card class="cartao-formulario">
            <q-card-section class="row items-center q-pb-sm">
              <div class="text-h6">
                {{ editando ? 'Editar usuário' : 'Novo usuário' }}
              </div>

              <q-space />

              <q-btn v-close-popup flat round dense icon="close" />
            </q-card-section>

            <q-separator />

            <q-card-section class="q-gutter-md">
              <q-banner
                v-if="erroFormulario"
                dense
                class="bg-red-1 text-negative"
                rounded
              >
                {{ erroFormulario }}
              </q-banner>

              <q-input
                v-model="formulario.usuario"
                outlined
                dense
                label="Usuário (login)"
                hint="É o que a pessoa digita para entrar"
              />

              <q-input
                v-model="formulario.nome"
                outlined
                dense
                label="Nome completo"
              />

              <q-input
                v-model="formulario.senha"
                outlined
                dense
                type="password"
                autocomplete="new-password"
                :label="editando ? 'Nova senha (deixe em branco para manter)' : 'Senha'"
                :hint="`Mínimo de ${SENHA_MINIMA} caracteres`"
              />

              <q-select
                v-model="formulario.nivel"
                outlined
                dense
                emit-value
                map-options
                label="Nível de acesso"
                :options="opcoesNiveis"
              />

              <q-toggle
                v-model="formulario.ativo"
                label="Usuário ativo"
                :disable="editando && formulario.id === usuario?.id"
              />

              <!-- ------------------------------------------- -->
              <!-- VÍNCULOS -->
              <!-- ------------------------------------------- -->

              <q-separator />

              <div>
                <div class="text-subtitle2">Vínculos</div>

                <div class="text-caption text-grey-7 q-mb-sm">
                  <template v-if="nivelIgnoraVinculos">
                    O nível
                    <strong>{{ rotuloDoNivel(formulario.nivel) }}</strong>
                    enxerga todas as equipes — vínculos não se aplicam.
                  </template>

                  <template v-else>
                    Sem nenhum vínculo, a pessoa enxerga todas as equipes.
                    Escolha valores para restringir.
                  </template>
                </div>

                <div v-if="!nivelIgnoraVinculos" class="q-gutter-md">
                  <q-select
                    v-for="(rotulo, tipo) in tiposVinculo"
                    :key="tipo"
                    v-model="formulario.vinculos[tipo]"
                    outlined
                    dense
                    multiple
                    use-chips
                    use-input
                    new-value-mode="add-unique"
                    input-debounce="0"
                    :label="rotulo"
                    :options="opcoesVinculo[tipo] || []"
                  />
                </div>
              </div>
            </q-card-section>

            <q-separator />

            <q-card-actions align="right">
              <q-btn v-close-popup flat label="Cancelar" />

              <q-btn
                color="primary"
                :label="editando ? 'Salvar' : 'Criar'"
                :loading="salvando"
                @click="salvar"
              />
            </q-card-actions>
          </q-card>
        </q-dialog>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

import CabecalhoApp from '../components/CabecalhoApp.vue'
import { PODE_GERENCIAR_USUARIOS, useSessao } from '../composables/useSessao'

definePage({ meta: { permissao: PODE_GERENCIAR_USUARIOS } })

const { usuario, niveis, tiposVinculo, buscarSessao } = useSessao()

const SENHA_MINIMA = 6

// mesmos nomes do auth.py
const PERMISSOES = [
  { valor: 'ver_resumo', rotulo: 'Ver resumo' },
  { valor: 'ver_equipes', rotulo: 'Ver equipes' },
  { valor: 'alocar', rotulo: 'Alocar' },
  { valor: 'gerenciar_vagas', rotulo: 'Cadastrar vagas' },
  { valor: 'gerenciar_usuarios', rotulo: 'Gerenciar usuários' }
]

const usuarios = ref([])
const equipes = ref([])
const carregando = ref(false)
const erro = ref('')
const sucesso = ref('')

const dialogAberto = ref(false)
const editando = ref(false)
const salvando = ref(false)
const erroFormulario = ref('')

const formulario = reactive({
  id: null,
  usuario: '',
  nome: '',
  senha: '',
  nivel: '',
  ativo: true,
  vinculos: {}
})

const opcoesNiveis = computed(() =>
  niveis.value.map(nivel => ({ label: nivel.rotulo, value: nivel.valor }))
)

const nivelIgnoraVinculos = computed(
  () =>
    niveis.value.find(nivel => nivel.valor === formulario.nivel)
      ?.ignora_vinculos ?? false
)

// Sugestões vindas do que já está cadastrado nas vagas, para não digitar
// setor e supervisor de novo — mas o campo aceita texto novo também.
const opcoesVinculo = computed(() => {
  const mapa = {
    BASE: new Set(),
    TIPO_EQUIPE: new Set(),
    SETOR: new Set(),
    SUPERVISOR: new Set(),
    COORDENADOR: new Set()
  }

  for (const equipe of equipes.value) {
    if (equipe.base) {
      mapa.BASE.add(String(equipe.base).trim())
    }

    for (const vaga of equipe.vagas || []) {
      const tipo = String(vaga.tipo || '').trim()
      if (tipo) {
        mapa.TIPO_EQUIPE.add(tipo)
      }

      for (const campo of ['setor', 'supervisor', 'coordenador']) {
        const valor = String(vaga[campo] || '').trim()

        if (valor) {
          mapa[campo.toUpperCase()].add(valor)
        }
      }
    }
  }

  return Object.fromEntries(
    Object.entries(mapa).map(([tipo, valores]) => [
      tipo,
      [...valores].sort((a, b) => a.localeCompare(b, 'pt-BR'))
    ])
  )
})

function rotuloDoNivel(valor) {
  return niveis.value.find(nivel => nivel.valor === valor)?.rotulo || valor
}

function resumoVinculos(pessoa) {
  const partes = Object.entries(pessoa.vinculos || {})
    .filter(([, valores]) => valores.length)
    .map(([tipo, valores]) => `${tiposVinculo.value[tipo] || tipo}: ${valores.join(', ')}`)

  return partes.join(' · ')
}

function limparAvisos() {
  erro.value = ''
  sucesso.value = ''
}

async function carregarTudo() {
  carregando.value = true
  limparAvisos()

  try {
    const [respostaUsuarios, respostaEquipes] = await Promise.all([
      fetch('/api/usuarios'),
      fetch('/api/equipes')
    ])

    const dadosUsuarios = await respostaUsuarios.json()

    if (!respostaUsuarios.ok || dadosUsuarios.erro) {
      throw new Error(dadosUsuarios.erro || 'Erro ao carregar os usuários.')
    }

    usuarios.value = dadosUsuarios

    // as sugestões de vínculo são um extra: se falharem, a tela segue
    const dadosEquipes = await respostaEquipes.json()
    equipes.value = Array.isArray(dadosEquipes) ? dadosEquipes : []
  } catch (e) {
    erro.value = e.message || 'Erro ao carregar os usuários.'
  } finally {
    carregando.value = false
  }
}

function preencher(pessoa) {
  formulario.id = pessoa?.id ?? null
  formulario.usuario = pessoa?.usuario || ''
  formulario.nome = pessoa?.nome || ''
  formulario.senha = ''
  formulario.nivel = pessoa?.nivel || niveis.value[0]?.valor || ''
  formulario.ativo = pessoa ? pessoa.ativo : true
  formulario.vinculos = Object.fromEntries(
    Object.keys(tiposVinculo.value).map(tipo => [
      tipo,
      [...(pessoa?.vinculos?.[tipo] || [])]
    ])
  )
}

function abrirNovo() {
  erroFormulario.value = ''
  editando.value = false
  preencher(null)
  dialogAberto.value = true
}

function abrirEdicao(pessoa) {
  erroFormulario.value = ''
  editando.value = true
  preencher(pessoa)
  dialogAberto.value = true
}

async function salvar() {
  erroFormulario.value = ''
  salvando.value = true

  try {
    const corpo = {
      usuario: formulario.usuario.trim(),
      nome: formulario.nome.trim(),
      nivel: formulario.nivel,
      ativo: formulario.ativo,
      vinculos: nivelIgnoraVinculos.value ? {} : formulario.vinculos
    }

    if (formulario.senha) {
      corpo.senha = formulario.senha
    }

    const resposta = await fetch(
      editando.value ? `/api/usuarios/${formulario.id}` : '/api/usuarios',
      {
        method: editando.value ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(corpo)
      }
    )

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Não foi possível salvar o usuário.')
    }

    dialogAberto.value = false
    sucesso.value = editando.value ? 'Usuário atualizado.' : 'Usuário criado.'

    await carregarTudo()

    // se a pessoa mexeu no próprio cadastro, o menu precisa refletir isso
    if (formulario.id === usuario.value?.id) {
      await buscarSessao()
    }
  } catch (e) {
    erroFormulario.value = e.message || 'Não foi possível salvar o usuário.'
  } finally {
    salvando.value = false
  }
}

async function removerUsuario(pessoa) {
  const confirmado = window.confirm(
    `Excluir o usuário "${pessoa.nome}" (${pessoa.usuario})?\n\n` +
      'Ele perde o acesso imediatamente. Isso não pode ser desfeito.'
  )

  if (!confirmado) {
    return
  }

  limparAvisos()

  try {
    const resposta = await fetch(`/api/usuarios/${pessoa.id}`, {
      method: 'DELETE'
    })

    const dados = await resposta.json()

    if (!resposta.ok || dados.erro) {
      throw new Error(dados.erro || 'Não foi possível remover o usuário.')
    }

    sucesso.value = 'Usuário removido.'
    await carregarTudo()
  } catch (e) {
    erro.value = e.message || 'Não foi possível remover o usuário.'
  }
}

// trocar para um nível que ignora vínculos limpa o que estava escolhido
watch(nivelIgnoraVinculos, ignora => {
  if (ignora) {
    for (const tipo of Object.keys(formulario.vinculos)) {
      formulario.vinculos[tipo] = []
    }
  }
})

onMounted(carregarTudo)
</script>

<style scoped>
.cartao-formulario {
  width: 100%;
  max-width: 520px;
}

.tabela-niveis :deep(th) {
  font-family: var(--fonte-ui);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-size: 0.72rem;
}
</style>
