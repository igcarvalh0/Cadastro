<template>
  <div class="marca-dagua-app" aria-hidden="true">
    <img src="/icons/logo-fundo.png" alt="" />
  </div>
</template>

<script setup>
// So decorativo: o losango da CGB, bem discreto, atras do conteudo real da
// tela. Mesmo arquivo usado no fundo da tela de login.
</script>

<style scoped>
.marca-dagua-app {
  position: fixed;
  right: -12%;
  bottom: -18%;
  width: min(66vw, 900px);
  height: min(66vw, 900px);
  opacity: 0.035;
  pointer-events: none;
  z-index: -1;
}

.marca-dagua-app img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>

<!--
  Fora do "scoped" de proposito: dentro dele, o compilador deste projeto
  descarta a parte da direita de "'':global(body.body--dark) .algo { ... }" e
  aplica a propriedade no <body> inteiro. Aqui isso deixava a pagina toda com
  opacity 0.06 no modo escuro — e, como o CSS de um componente continua
  valendo depois de carregado, o estrago vazava ate para a tela de login.
-->
<style>
body.body--dark .marca-dagua-app {
  opacity: 0.06;
}
</style>
