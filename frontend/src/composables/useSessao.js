import { computed, ref } from 'vue'

// Estado fora da função: quem está logado é um dado só, compartilhado por
// todas as telas e pelo guarda de rota.
const usuario = ref(null)
const niveis = ref([])
const tiposVinculo = ref({})
const setoresNegocio = ref([])
const carregada = ref(false)

let carregamentoEmAndamento = null

async function buscarSessao() {
  const resposta = await fetch('/api/sessao')
  const dados = await resposta.json()

  usuario.value = dados.autenticado ? dados.usuario : null
  niveis.value = dados.niveis || []
  tiposVinculo.value = dados.tipos_vinculo || {}
  setoresNegocio.value = dados.setores_negocio || []
  carregada.value = true

  return usuario.value
}

/**
 * Garante que a sessão foi consultada uma vez. Chamadas simultâneas (o guarda
 * de rota e a tela, por exemplo) compartilham a mesma requisição.
 */
async function garantirSessao() {
  if (carregada.value) {
    return usuario.value
  }

  carregamentoEmAndamento =
    carregamentoEmAndamento ||
    buscarSessao().finally(() => {
      carregamentoEmAndamento = null
    })

  return carregamentoEmAndamento
}

async function entrar(login, senha) {
  const resposta = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario: login, senha })
  })

  const dados = await resposta.json()

  if (!resposta.ok || dados.erro) {
    throw new Error(dados.erro || 'Não foi possível entrar.')
  }

  // relê a sessão para trazer também níveis e tipos de vínculo
  await buscarSessao()

  return usuario.value
}

async function sair() {
  try {
    await fetch('/api/logout', { method: 'POST' })
  } finally {
    usuario.value = null
    carregada.value = true
  }
}

/** Chamado quando a API responde 401: a sessão caiu por trás da tela. */
function marcarSessaoExpirada() {
  usuario.value = null
  carregada.value = true
}

export function useSessao() {
  return {
    usuario,
    niveis,
    tiposVinculo,
    setoresNegocio,
    autenticado: computed(() => Boolean(usuario.value)),
    temPermissao: permissao =>
      Boolean(usuario.value?.permissoes?.includes(permissao)),
    garantirSessao,
    buscarSessao,
    entrar,
    sair,
    marcarSessaoExpirada
  }
}

// Permissões, iguais às do auth.py
export const PODE_VER_RESUMO = 'ver_resumo'
export const PODE_VER_EQUIPES = 'ver_equipes'
export const PODE_ALOCAR = 'alocar'
export const PODE_EDITAR_ALOCACAO = 'editar_alocacao'
export const PODE_REMOVER_ALOCACAO = 'remover_alocacao'
export const PODE_GERENCIAR_VAGAS = 'gerenciar_vagas'
export const PODE_GERENCIAR_USUARIOS = 'gerenciar_usuarios'
export const PODE_GERENCIAR_COLABORADORES = 'gerenciar_colaboradores'
