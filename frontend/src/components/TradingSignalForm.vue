<template>
  <div class="trading-signal-form">
    <h3>提交交易信号</h3>
    <form @submit.prevent="submitSignal">
      <div class="form-group">
        <label>交易ID</label>
        <input v-model="signal.trade_id" type="text" required>
      </div>
      <div class="form-group">
        <label>策略名称</label>
        <input v-model="signal.title" type="text" required>
      </div>
      <div class="form-group">
        <label>交易对</label>
        <select v-model="signal.currency" required>
          <option value="BTCUSDT">BTC/USDT</option>
          <option value="ETHUSDT">ETH/USDT</option>
        </select>
      </div>
      <div class="form-group">
        <label>止损价</label>
        <input v-model.number="signal.zs_tp_trigger_px" type="number" step="0.01" required>
      </div>
      <div class="form-group">
        <label>止盈价</label>
        <div v-for="(price, index) in signal.zy_tp_trigger_px" :key="index">
          <input v-model.number="signal.zy_tp_trigger_px[index]" type="number" step="0.01">
          <button type="button" @click="removeStopProfit(index)">删除</button>
        </div>
        <button type="button" @click="addStopProfit">添加止盈价</button>
      </div>
      <div class="form-group">
        <label>杠杆倍数</label>
        <input v-model.number="signal.lever" type="number" required>
      </div>
      <div class="form-group">
        <label>交易方向</label>
        <select v-model="signal.side" required>
          <option value="buy">做多</option>
          <option value="sell">做空</option>
        </select>
      </div>
      <button type="submit">提交信号</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      signal: {
        trade_id: '',
        title: '',
        currency: 'BTCUSDT',
        zs_tp_trigger_px: 0,
        zy_tp_trigger_px: [0],
        lever: 1,
        side: 'buy',
        is_close: false
      }
    }
  },
  methods: {
    addStopProfit() {
      this.signal.zy_tp_trigger_px.push(0)
    },
    removeStopProfit(index) {
      this.signal.zy_tp_trigger_px.splice(index, 1)
    },
    async submitSignal() {
      try {
        const response = await fetch('http://localhost:8000/api/signals', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.signal)
        })
        if (response.ok) {
          this.$emit('signal-created')
          this.resetForm()
        }
      } catch (error) {
        console.error('Error submitting signal:', error)
      }
    },
    resetForm() {
      this.signal = {
        trade_id: '',
        title: '',
        currency: 'BTCUSDT',
        zs_tp_trigger_px: 0,
        zy_tp_trigger_px: [0],
        lever: 1,
        side: 'buy',
        is_close: false
      }
    }
  }
}
</script>

<style scoped>
.trading-signal-form {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input, select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  background-color: #4CAF50;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #45a049;
}
</style> 