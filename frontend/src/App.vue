<template>
  <div id="app">
    <AgentChat />
  </div>
</template>

<script setup>
import AgentChat from './components/AgentChat.vue'
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #0f0f0f;
  color: #f0f0f0;
  height: 100vh;
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
