<template>
  <div class="trading-signals">
    <h2>交易信号列表</h2>
    <table>
      <thead>
        <tr>
          <th>交易ID</th>
          <th>策略名称</th>
          <th>交易对</th>
          <th>实时价格</th>
          <th>止损价</th>
          <th>止盈价</th>
          <th>杠杆</th>
          <th>方向</th>
          <th>状态</th>
          <th>收益率</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="signal in signals" :key="signal.trade_id">
          <td>{{ signal.trade_id }}</td>
          <td>{{ signal.title }}</td>
          <td>{{ signal.currency }}</td>
          <td>{{ realTimePrices[signal.currency] || '-' }}</td>
          <td>{{ signal.zs_tp_trigger_px }}</td>
          <td>{{ signal.zy_tp_trigger_px.join(', ') }}</td>
          <td>{{ signal.lever }}x</td>
          <td>{{ signal.side === 'buy' ? '做多' : '做空' }}</td>
          <td>{{ signal.is_close ? '已平仓' : '持仓中' }}</td>
          <td>{{ signal.profit_percentage ? signal.profit_percentage.toFixed(2) + '%' : '-' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      signals: [],
      realTimePrices: {},
      ws: null
    }
  },
  async created() {
    await this.fetchSignals()
    this.connectWebSocket()
  },
  methods: {
    async fetchSignals() {
      try {
        const response = await fetch('http://localhost:8000/api/signals')
        this.signals = await response.json()
      } catch (error) {
        console.error('Error fetching signals:', error)
      }
    },
    connectWebSocket() {
      const symbols = new Set(this.signals.map(s => s.currency.toLowerCase()))
      symbols.forEach(symbol => {
        const ws = new WebSocket(`ws://localhost:8000/ws/${symbol}`)
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data)
          this.realTimePrices[data.symbol] = data.price
        }
      })
    }
  }
}
</script> 