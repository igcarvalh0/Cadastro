<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="cabecalho-login">
      <q-toolbar>
        <div class="site-logo q-mr-sm">
          <img src="/icons/logo-login.png" alt="CGB Energia" />
        </div>

        <q-toolbar-title>
          <div class="cabecalho-login__titulo">Gerenciador de Equipes</div>
          <div class="cabecalho-login__subtitulo">Setor de Medição · CGB Energia</div>
        </q-toolbar-title>

        <div
          class="selo-status q-mr-sm"
          :class="{ 'selo-status--offline': servidorOnline === false }"
        >
          <span class="selo-status__ponto" />
          {{ seloStatusTexto }}
        </div>

        <q-btn
          flat
          round
          dense
          :icon="modoNoturno ? 'light_mode' : 'dark_mode'"
          aria-label="Alternar tema"
          @click="alternarModoNoturno"
        >
          <q-tooltip>{{ modoNoturno ? 'Modo claro' : 'Modo noturno' }}</q-tooltip>
        </q-btn>

        <q-btn
          flat
          round
          dense
          icon="help_outline"
          aria-label="Ajuda"
          @click="ajudaAberta = true"
        >
          <q-tooltip>Ajuda</q-tooltip>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="tela-login flex flex-center q-pa-md">
        <canvas ref="canvasFundoEl" class="canvas-fundo" aria-hidden="true"></canvas>

        <div class="marca-dagua" aria-hidden="true">
          <img src="/icons/logo-fundo.png" alt="" />
        </div>

        <div class="conteudo-login">
          <div class="coluna-mensagem">
            <div class="selo-seguranca">
              <q-icon name="verified_user" size="16px" />
              Acesso restrito às equipes autorizadas
            </div>

            <h1 class="titulo-hero">
              Gestão de<br />
              <span class="titulo-hero__destaque">Equipes de Campo</span>
            </h1>

            <p class="texto-hero">
              Acompanhe alocações, vagas e o resumo operacional das equipes do
              setor de medição em um só lugar.
            </p>
          </div>

          <div class="cartao-login-halo">
          <q-card bordered class="cartao-login">
            <div class="cartao-login__faixa"></div>

            <q-card-section class="text-center q-pb-none">
              <div class="marca-login">
                <img src="/icons/logo-login.png" alt="CGB Energia" />
              </div>

              <div class="text-h6 titulo-cartao">
                {{ modoRecuperacao ? 'Recuperar acesso' : 'Entrar no sistema' }}
              </div>

              <div class="text-caption text-grey-7">
                {{
                  modoRecuperacao
                    ? 'Veja como redefinir sua senha'
                    : 'Entre com o seu usuário para continuar'
                }}
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

              <!-- ------------------------------------------- -->
              <!-- LOGIN -->
              <!-- ------------------------------------------- -->
              <q-form v-if="!modoRecuperacao" @submit.prevent="autenticar">
                <q-input
                  v-model="login"
                  outlined
                  dense
                  autofocus
                  class="q-mb-md"
                  label="Usuário"
                  autocomplete="username"
                  :disable="entrando"
                >
                  <template #prepend>
                    <q-icon name="badge" />
                  </template>
                </q-input>

                <q-input
                  v-model="senha"
                  outlined
                  dense
                  class="q-mb-sm"
                  label="Senha"
                  autocomplete="current-password"
                  :type="mostrarSenha ? 'text' : 'password'"
                  :disable="entrando"
                >
                  <template #prepend>
                    <q-icon name="key" />
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

                <div class="text-right q-mb-md">
                  <a href="#" class="link-recuperar" @click.prevent="modoRecuperacao = true">
                    Esqueceu a senha?
                  </a>
                </div>

                <q-btn
                  type="submit"
                  color="primary"
                  class="full-width botao-entrar"
                  label="Entrar no sistema"
                  icon-right="arrow_forward"
                  :loading="entrando"
                  :disable="!login || !senha"
                />
              </q-form>

              <!-- ------------------------------------------- -->
              <!-- RECUPERAR ACESSO -->
              <!-- ------------------------------------------- -->
              <div v-else class="q-gutter-md">
                <p class="text-body2 text-grey-8">
                  Ainda não existe redefinição automática por e-mail neste
                  sistema. Procure o administrador (nível Mestre) do
                  Gerenciador de Equipes para redefinir a sua senha.
                </p>

                <q-btn
                  flat
                  class="full-width"
                  label="Voltar para o login"
                  icon="arrow_back"
                  @click="modoRecuperacao = false"
                />
              </div>
            </q-card-section>
          </q-card>
          </div>
        </div>

        <!-- ------------------------------------------- -->
        <!-- NOTIFICAÇÕES -->
        <!-- ------------------------------------------- -->
        <div class="toasts-login">
          <transition-group name="toast-login">
            <div
              v-for="item in toasts"
              :key="item.id"
              class="toast-login"
              :class="`toast-login--${item.tipo}`"
            >
              <q-icon :name="iconeDoToast(item.tipo)" />
              <span class="toast-login__texto">{{ item.texto }}</span>
              <q-btn flat round dense size="sm" icon="close" @click="fecharToast(item.id)" />
            </div>
          </transition-group>
        </div>

        <!-- ------------------------------------------- -->
        <!-- AJUDA -->
        <!-- ------------------------------------------- -->
        <q-dialog v-model="ajudaAberta">
          <q-card class="cartao-ajuda">
            <q-card-section class="row items-center q-pb-sm">
              <q-icon name="support_agent" size="28px" class="q-mr-sm text-primary" />
              <div class="text-h6">Suporte</div>
              <q-space />
              <q-btn v-close-popup flat round dense icon="close" />
            </q-card-section>

            <q-separator />

            <q-card-section class="text-body2">
              Para dúvidas de acesso, senha ou vínculo com sua equipe, procure
              o administrador do sistema (nível Mestre) no setor de medição.
            </q-card-section>

            <q-card-actions align="right">
              <q-btn v-close-popup color="primary" label="Entendido" />
            </q-card-actions>
          </q-card>
        </q-dialog>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
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
const modoRecuperacao = ref(false)
const ajudaAberta = ref(false)

// marcado pelo boot quando a API respondeu 401 no meio do uso
const sessaoExpirou = computed(() => route.query.expirou === '1')

async function autenticar() {
  entrando.value = true

  try {
    await entrar(login.value.trim(), senha.value)
    avisar('Login efetuado com sucesso.', 'sucesso')

    // volta para a tela que a pessoa tentou abrir antes do login
    const destino = route.query.destino
    await router.replace(
      typeof destino === 'string' && destino !== '/login' ? destino : '/'
    )
  } catch (e) {
    avisar(e.message || 'Não foi possível entrar.', 'erro')
    senha.value = ''
  } finally {
    entrando.value = false
  }
}

// ============================================================
// NOTIFICAÇÕES (toasts)
// ============================================================

const toasts = ref([])
let proximoIdToast = 1

function iconeDoToast(tipo) {
  if (tipo === 'sucesso') return 'check_circle'
  if (tipo === 'erro') return 'error'
  return 'info'
}

function avisar(texto, tipo = 'info') {
  const id = proximoIdToast++
  toasts.value.push({ id, texto, tipo })
  setTimeout(() => fecharToast(id), 4000)
}

function fecharToast(id) {
  toasts.value = toasts.value.filter(item => item.id !== id)
}

// ============================================================
// STATUS DO SERVIDOR
// ============================================================

const servidorOnline = ref(null)

const seloStatusTexto = computed(() => {
  if (servidorOnline.value === null) return 'Verificando…'
  return servidorOnline.value ? 'Sistema online' : 'Sem conexão'
})

async function verificarServidor() {
  try {
    const resposta = await fetch('/api/status')
    servidorOnline.value = resposta.ok
  } catch {
    servidorOnline.value = false
  }
}

// ============================================================
// FUNDO ANIMADO
// ============================================================
// Fundo discreto e decorativo: uma rede de pontos conectados (estilo
// "plexus") nas cores da marca, com pequenos losangos (o icone da CGB)
// flutuando por cima. Nao carrega nada de fora — so canvas 2D nativo.

const canvasFundoEl = ref(null)
let contextoFundo = null
let quadroAnimacao = null
let tempoFundo = 0

const ladrilhos = [
  { x: -1, y: -1, cor: '#8E1834' },
  { x: 0, y: -1, cor: '#6B1025' },
  { x: 1, y: -1, cor: '#7D132C' },
  { x: -1, y: 0, cor: '#9F1C3C' },
  { x: 1, y: 0, cor: '#7D132C' },
  { x: -1, y: 1, cor: '#8E1834' },
  { x: 0, y: 1, cor: '#5D0C1E' },
  { x: 1, y: 1, cor: '#6B1025' }
]

// Rede tipo "plexus": pontos flutuando bem devagar, ligados por linhas finas
// quando ficam proximos — como uma malha de conexoes formando triangulos,
// no estilo de fundo de "rede/tecnologia". Nas cores da marca.
const REDE_NUM_PONTOS = 100
const REDE_DISTANCIA_LINHA = 275
const REDE_COR_LINHA = '213, 77, 110'
const REDE_COR_PONTO = '229, 124, 148'
const REDE_COR_DESTAQUE = '255, 214, 224'

let pontosRede = []

function criarPontoRede(largura, altura, destaque) {
  const angulo = Math.random() * Math.PI * 2
  const velocidade = destaque ? 0.12 + Math.random() * 0.1 : 0.06 + Math.random() * 0.14

  return {
    x: Math.random() * largura,
    y: Math.random() * altura,
    vx: Math.cos(angulo) * velocidade,
    vy: Math.sin(angulo) * velocidade,
    raio: destaque ? 2.6 + Math.random() * 1 : 1.3 + Math.random() * 1,
    pulso: Math.random() * Math.PI * 2,
    destaque
  }
}

function prepararRede(largura, altura) {
  pontosRede = Array.from({ length: REDE_NUM_PONTOS }, (_, i) =>
    criarPontoRede(largura, altura, i % 7 === 0)
  )
}

let particulas = []

function prepararParticulas(largura, altura) {
  particulas = Array.from({ length: 26 }, () => ({
    x: Math.random() * largura,
    y: Math.random() * altura,
    escala: Math.random() * 0.16 + 0.06,
    velocidade: Math.random() * 0.5 + 0.2,
    opacidade: Math.random() * 0.25 + 0.08,
    pulso: Math.random() * Math.PI
  }))
}

function desenharLosango(ctx, centroX, centroY, escala, opacidade, rotacao) {
  ctx.save()
  ctx.translate(centroX, centroY)
  ctx.rotate(rotacao)
  ctx.globalAlpha = opacidade

  const tamanho = 24 * escala
  const espaco = 26 * escala

  for (const ladrilho of ladrilhos) {
    ctx.fillStyle = ladrilho.cor
    ctx.beginPath()
    ctx.roundRect(
      ladrilho.x * espaco - tamanho / 2,
      ladrilho.y * espaco - tamanho / 2,
      tamanho,
      tamanho,
      2 * escala
    )
    ctx.fill()
  }

  ctx.restore()
}

function desenharRede(ctx, largura, altura) {
  if (!largura || !altura) return

  // move e faz quicar nas bordas, bem devagar
  for (const ponto of pontosRede) {
    ponto.x += ponto.vx
    ponto.y += ponto.vy
    ponto.pulso += 0.02

    if (ponto.x < 0 || ponto.x > largura) ponto.vx *= -1
    if (ponto.y < 0 || ponto.y > altura) ponto.vy *= -1

    ponto.x = Math.min(Math.max(ponto.x, 0), largura)
    ponto.y = Math.min(Math.max(ponto.y, 0), altura)
  }

  // liga os pontos proximos com linhas finas — quanto mais perto, mais viva
  for (let i = 0; i < pontosRede.length; i++) {
    for (let j = i + 1; j < pontosRede.length; j++) {
      const a = pontosRede[i]
      const b = pontosRede[j]
      const dx = a.x - b.x
      const dy = a.y - b.y
      const distancia = Math.sqrt(dx * dx + dy * dy)

      if (distancia < REDE_DISTANCIA_LINHA) {
        const alpha = (1 - distancia / REDE_DISTANCIA_LINHA) * 0.45
        ctx.strokeStyle = `rgba(${REDE_COR_LINHA}, ${alpha.toFixed(3)})`
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(a.x, a.y)
        ctx.lineTo(b.x, b.y)
        ctx.stroke()
      }
    }
  }

  // pontos por cima das linhas, com um leve brilho
  for (const ponto of pontosRede) {
    const cor = ponto.destaque ? REDE_COR_DESTAQUE : REDE_COR_PONTO
    const opacidade = ponto.destaque
      ? 0.7 + Math.sin(ponto.pulso) * 0.25
      : 0.35 + Math.sin(ponto.pulso) * 0.15

    ctx.save()
    ctx.shadowColor = `rgba(${cor}, 0.9)`
    ctx.shadowBlur = ponto.destaque ? 8 : 3
    ctx.fillStyle = `rgba(${cor}, ${Math.max(0.15, opacidade).toFixed(3)})`
    ctx.beginPath()
    ctx.arc(ponto.x, ponto.y, ponto.raio, 0, Math.PI * 2)
    ctx.fill()
    ctx.restore()
  }
}

function animarFundo() {
  const canvas = canvasFundoEl.value
  if (!canvas || !contextoFundo) return

  tempoFundo += 0.008

  contextoFundo.clearRect(0, 0, canvas.width, canvas.height)
  desenharRede(contextoFundo, canvas.width, canvas.height)

  particulas.forEach((particula, indice) => {
    const anguloAtual = -0.55 + Math.sin(tempoFundo + indice) * 0.15
    particula.x += Math.cos(anguloAtual) * particula.velocidade
    particula.y += Math.sin(anguloAtual) * particula.velocidade
    particula.pulso += 0.02

    const opacidadeAtual = particula.opacidade + Math.sin(particula.pulso) * 0.04

    if (
      particula.x > canvas.width + 120 ||
      particula.y > canvas.height + 120 ||
      particula.x < -120 ||
      particula.y < -120
    ) {
      particula.x = Math.random() * canvas.width * 0.8 - 100
      particula.y = -80
    }

    desenharLosango(
      contextoFundo,
      particula.x,
      particula.y,
      particula.escala,
      Math.max(0.02, opacidadeAtual),
      anguloAtual + Math.PI / 4
    )
  })

  quadroAnimacao = requestAnimationFrame(animarFundo)
}

function redimensionarCanvas() {
  const canvas = canvasFundoEl.value
  if (!canvas) return

  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  prepararParticulas(canvas.width, canvas.height)
  prepararRede(canvas.width, canvas.height)
}

onMounted(async () => {
  restaurarModoNoturno()
  verificarServidor()

  await nextTick()

  if (canvasFundoEl.value) {
    contextoFundo = canvasFundoEl.value.getContext('2d')
    redimensionarCanvas()
    window.addEventListener('resize', redimensionarCanvas)
    quadroAnimacao = requestAnimationFrame(animarFundo)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', redimensionarCanvas)
  if (quadroAnimacao) cancelAnimationFrame(quadroAnimacao)
})
</script>

<style scoped>
/* ============================================================ */
/* CABEÇALHO */
/* ============================================================ */

.cabecalho-login {
  background: rgba(255, 255, 255, 0.85);
  color: var(--tinta);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--linha);
  box-shadow: none;
}

.cabecalho-login__titulo {
  font-family: 'Inter', var(--fonte-ui);
  font-weight: 800;
  font-size: 1.05rem;
  letter-spacing: -0.01em;
  color: var(--titulo);
}

.cabecalho-login__subtitulo {
  font-family: 'Inter', var(--fonte-texto);
  font-weight: 500;
  font-size: 0.7rem;
  letter-spacing: 0.02em;
  color: var(--tinta-fraca);
  text-transform: uppercase;
}

.selo-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(27, 107, 69, 0.1);
  color: var(--positivo);
  font-family: 'Inter', var(--fonte-texto);
  font-size: 0.7rem;
  font-weight: 600;
  border: 1px solid rgba(27, 107, 69, 0.2);
}

.selo-status__ponto {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
  animation: pulsar-selo 2s ease-in-out infinite;
}

.selo-status--offline {
  background: rgba(179, 38, 30, 0.1);
  color: var(--negativo);
  border-color: rgba(179, 38, 30, 0.2);
}

.selo-status--offline .selo-status__ponto {
  animation: none;
}

@keyframes pulsar-selo {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

/* ============================================================ */
/* FUNDO */
/* ============================================================ */

.tela-login {
  background: var(--fundo);
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.canvas-fundo {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.marca-dagua {
  position: fixed;
  top: 50%;
  left: -14%;
  transform: translateY(-50%);
  width: min(72vw, 980px);
  height: min(72vw, 980px);
  opacity: 0.08;
  pointer-events: none;
  z-index: 0;
}

.marca-dagua img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* ============================================================ */
/* CONTEÚDO */
/* ============================================================ */

.conteudo-login {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 980px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
  align-items: center;
  padding: 24px 0;
}

@media (min-width: 900px) {
  .conteudo-login {
    grid-template-columns: 1.05fr 1fr;
  }
}

.coluna-mensagem {
  display: none;
  flex-direction: column;
  gap: 18px;
}

@media (min-width: 900px) {
  .coluna-mensagem {
    display: flex;
  }
}

.selo-seguranca {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  width: fit-content;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(113, 20, 36, 0.08);
  border: 1px solid rgba(113, 20, 36, 0.18);
  color: var(--marca-clara);
  font-family: 'Inter', var(--fonte-texto);
  font-weight: 600;
  font-size: 0.75rem;
}

.titulo-hero {
  font-family: 'Inter', var(--fonte-ui);
  font-weight: 800;
  font-size: 2.2rem;
  line-height: 1.15;
  letter-spacing: -0.01em;
  color: var(--titulo);
  margin: 0;
}

.titulo-hero__destaque {
  background: linear-gradient(90deg, var(--marca) 0%, var(--marca-clara) 60%, #e57c94 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.texto-hero {
  font-family: 'Inter', var(--fonte-texto);
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--tinta-fraca);
  max-width: 40ch;
  margin: 0;
}

/* ============================================================ */
/* CARTÃO DE LOGIN */
/* ============================================================ */

.cartao-login-halo {
  position: relative;
  width: 100%;
  max-width: 399px;
  margin: 0 auto;
}

/* brilho atras do cartao: reforca a sensacao de profundidade quando os
   feixes do fundo passam por tras, meio que "iluminando" o vidro */
.cartao-login-halo::before {
  content: '';
  position: absolute;
  inset: -34px;
  z-index: 0;
  background: radial-gradient(
    closest-side,
    rgba(213, 77, 110, 0.3),
    rgba(150, 27, 56, 0.12) 55%,
    transparent 75%
  );
  filter: blur(26px);
  pointer-events: none;
}

.cartao-login {
  position: relative;
  z-index: 1;
  width: 100%;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  /* sombra bem mais presente que o padrao do app: eh o que da a sensacao de
     o cartao estar flutuando acima dos feixes do fundo */
  box-shadow:
    0 30px 60px -15px rgba(37, 4, 13, 0.45),
    0 12px 24px -8px rgba(37, 4, 13, 0.3);
}

.cartao-login__faixa {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--marca) 0%, var(--marca-clara) 50%, #e57c94 100%);
}

.titulo-cartao {
  font-family: 'Inter', var(--fonte-ui);
  font-weight: 700;
  color: var(--titulo);
}

.marca-login img {
  /* a arte e um logo largo (1512x596px), nao um icone quadrado: largura fixa
     estica o desenho. Altura fixa + largura automatica preserva a proporcao
     real do arquivo, entao nunca distorce, mesmo se a arte for trocada. */
  height: 56px;
  width: auto;
  margin-bottom: 8px;
}

.link-recuperar {
  font-family: 'Inter', var(--fonte-texto);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--marca-clara);
  text-decoration: none;
}

.link-recuperar:hover {
  text-decoration: underline;
}

.botao-entrar {
  font-family: 'Inter', var(--fonte-ui);
}

/* ============================================================ */
/* NOTIFICAÇÕES */
/* ============================================================ */

.toasts-login {
  position: fixed;
  top: 76px;
  right: 16px;
  z-index: 3000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: min(90vw, 340px);
}

.toast-login {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  box-shadow: var(--sombra);
  border: 1px solid var(--linha);
  font-family: 'Inter', var(--fonte-texto);
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--tinta);
}

.toast-login__texto {
  flex: 1;
}

.toast-login--sucesso {
  border-color: rgba(27, 107, 69, 0.3);
  color: var(--positivo);
}

.toast-login--erro {
  border-color: rgba(179, 38, 30, 0.3);
  color: var(--negativo);
}

.toast-login-enter-active,
.toast-login-leave-active {
  transition: all 0.25s ease;
}

.toast-login-enter-from,
.toast-login-leave-to {
  opacity: 0;
  transform: translateX(24px);
}

/* ============================================================ */
/* AJUDA */
/* ============================================================ */

.cartao-ajuda {
  width: 100%;
  max-width: 380px;
}
</style>

<!--
  Ficou num bloco proprio, sem "scoped": o compilador do Vue/Vite deste
  projeto (vue-loader + lightningcss) estava DESCARTANDO a parte da direita
  em toda regra "'':global(body.body--dark) .algo { ... }" dentro do
  <style scoped> — o resultado compilado virava so "body.body--dark { ... }",
  aplicando as propriedades no <body> inteiro (foi assim, por exemplo, que um
  "opacity: 0.12" pensado para a marca d'agua acabou deixando a pagina
  inteira translucida no modo escuro). Fora do "scoped" essas regras nao
  passam por essa transformacao e funcionam normalmente.
-->
<style>
body.body--dark .cabecalho-login {
  background: rgba(15, 20, 30, 0.85);
  border-bottom-color: var(--linha);
}

body.body--dark .marca-dagua {
  opacity: 0.12;
}

body.body--dark .selo-seguranca {
  background: rgba(224, 138, 156, 0.1);
  border-color: rgba(224, 138, 156, 0.25);
  color: #e08a9c;
}

body.body--dark .link-recuperar {
  color: #e08a9c;
}

body.body--dark .cartao-login-halo::before {
  background: radial-gradient(
    closest-side,
    rgba(224, 138, 156, 0.28),
    rgba(150, 27, 56, 0.14) 55%,
    transparent 75%
  );
}

body.body--dark .cartao-login {
  background: rgba(15, 20, 30, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow:
    0 30px 70px -12px rgba(0, 0, 0, 0.7),
    0 14px 28px -8px rgba(0, 0, 0, 0.55);
}

body.body--dark .toast-login {
  background: rgba(20, 24, 33, 0.92);
}
</style>
