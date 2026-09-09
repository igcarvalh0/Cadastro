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
  right: -8%;
  bottom: -10%;
  width: min(34vw, 440px);
  height: min(34vw, 440px);
  opacity: 0.035;
  pointer-events: none;
  z-index: -1;
}

:global(body.body--dark) .marca-dagua-app {
  opacity: 0.06;
}

.marca-dagua-app img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
