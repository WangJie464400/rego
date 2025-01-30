<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
}
</script>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  background: #121212;
  background: linear-gradient(135deg, #1f1f1f, #2c2c2c);
  font-family: 'Roboto', sans-serif;
  color: #ffffff;
}
</style>
