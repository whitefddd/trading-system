<template>
  <div id="app">
    <nav class="navbar">
      <h1>交易信号管理系统</h1>
    </nav>
    <div class="container">
      <SignalList />
    </div>
  </div>
</template>

<script>
import SignalList from './components/SignalList.vue'

export default {
  name: 'App',
  components: {
    SignalList
  }
}
</script>

<style>
#app {
  font-family: Arial, sans-serif;
}

.navbar {
  background-color: #2c3e50;
  color: white;
  padding: 1rem;
  margin-bottom: 2rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}
</style> 