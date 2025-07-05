<template>
  <div id="app">
    <StreamChat />
  </div>
</template>

<script setup>
import StreamChat from '@/components/StreamChat.vue';
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  background-color: #f3f4f6;
  color: #1f2937;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  line-height: 1.5;
}

#app {
  height: 100%;
  padding: 20px;
}
</style>