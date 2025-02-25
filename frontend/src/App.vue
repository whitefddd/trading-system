<template>
  <div id="app">
    <nav class="navbar">
      <h1>交易信号管理系统</h1>
    </nav>
    <div class="container">
      <TradingDashboard />
    </div>
  </div>
</template>

<script>
import TradingDashboard from './components/TradingDashboard.vue'

export default {
  name: 'App',
  components: {
    TradingDashboard
  }
}
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 20px;
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