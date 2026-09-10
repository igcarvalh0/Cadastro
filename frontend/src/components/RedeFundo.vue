<template>
  <canvas ref="canvasEl" class="rede-fundo" aria-hidden="true"></canvas>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

/**
 * Versão leve da rede de pontos que enfeita o fundo da tela de login.
 *
 * Aqui as telas têm tabela grande, filtro e rolagem, e ficam abertas o dia
 * todo — o enfeite não pode disputar CPU com o trabalho de verdade. Por isso
 * esta versão corta o que é caro no canvas: menos pontos, nenhum brilho
 * (shadowBlur) nos pontos, metade dos quadros por segundo, e ela para sozinha
 * quando a aba sai de foco ou quando o sistema pede menos animação.
 */

const PONTOS = 20
const DISTANCIA_LINHA = 150
const COR_LINHA = '213, 77, 110'
const COR_PONTO = '229, 124, 148'
const INTERVALO_QUADRO = 1000 / 30

const canvasEl = ref(null)

let contexto = null
let quadro = null
let pontos = []
let ultimoQuadro = 0
let animando = false

function preferoMenosAnimacao() {
  return window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
}

function prepararPontos(largura, altura) {
  pontos = Array.from({ length: PONTOS }, () => {
    const angulo = Math.random() * Math.PI * 2
    const velocidade = 0.05 + Math.random() * 0.1

    return {
      x: Math.random() * largura,
      y: Math.random() * altura,
      vx: Math.cos(angulo) * velocidade,
      vy: Math.sin(angulo) * velocidade,
      raio: 1.2 + Math.random() * 0.9
    }
  })
}

function desenhar() {
  const canvas = canvasEl.value
  if (!canvas || !contexto) return

  const largura = canvas.width
  const altura = canvas.height

  contexto.clearRect(0, 0, largura, altura)

  for (const ponto of pontos) {
    ponto.x += ponto.vx
    ponto.y += ponto.vy

    if (ponto.x < 0 || ponto.x > largura) ponto.vx *= -1
    if (ponto.y < 0 || ponto.y > altura) ponto.vy *= -1

    ponto.x = Math.min(Math.max(ponto.x, 0), largura)
    ponto.y = Math.min(Math.max(ponto.y, 0), altura)
  }

  contexto.lineWidth = 1

  for (let i = 0; i < pontos.length; i++) {
    for (let j = i + 1; j < pontos.length; j++) {
      const a = pontos[i]
      const b = pontos[j]
      const dx = a.x - b.x
      const dy = a.y - b.y
      const distancia = Math.sqrt(dx * dx + dy * dy)

      if (distancia < DISTANCIA_LINHA) {
        const alpha = (1 - distancia / DISTANCIA_LINHA) * 0.5
        contexto.strokeStyle = `rgba(${COR_LINHA}, ${alpha.toFixed(3)})`
        contexto.beginPath()
        contexto.moveTo(a.x, a.y)
        contexto.lineTo(b.x, b.y)
        contexto.stroke()
      }
    }
  }

  contexto.fillStyle = `rgba(${COR_PONTO}, 0.5)`

  for (const ponto of pontos) {
    contexto.beginPath()
    contexto.arc(ponto.x, ponto.y, ponto.raio, 0, Math.PI * 2)
    contexto.fill()
  }
}

function animar(agora) {
  if (!animando) return

  if (agora - ultimoQuadro >= INTERVALO_QUADRO) {
    ultimoQuadro = agora
    desenhar()
  }

  quadro = requestAnimationFrame(animar)
}

function iniciar() {
  if (animando || preferoMenosAnimacao()) return

  animando = true
  quadro = requestAnimationFrame(animar)
}

function parar() {
  animando = false

  if (quadro) {
    cancelAnimationFrame(quadro)
    quadro = null
  }
}

function aoTrocarVisibilidade() {
  if (document.hidden) parar()
  else iniciar()
}

function redimensionar() {
  const canvas = canvasEl.value
  if (!canvas) return

  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  prepararPontos(canvas.width, canvas.height)
  desenhar()
}

onMounted(() => {
  const canvas = canvasEl.value
  if (!canvas) return

  contexto = canvas.getContext('2d')
  // desenha um quadro logo de cara: quem pediu menos animação fica com a rede
  // parada, em vez de ficar sem fundo nenhum
  redimensionar()

  window.addEventListener('resize', redimensionar)
  document.addEventListener('visibilitychange', aoTrocarVisibilidade)

  iniciar()
})

onBeforeUnmount(() => {
  parar()
  window.removeEventListener('resize', redimensionar)
  document.removeEventListener('visibilitychange', aoTrocarVisibilidade)
})
</script>

<style scoped>
.rede-fundo {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: -1;
}
</style>
