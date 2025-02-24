<template>
  <div class="history-modal" v-if="show">
    <div class="modal-content">
      <h3>{{ title }} - 历史记录</h3>
      <table>
        <thead>
          <tr>
            <th>交易对</th>
            <th>开仓价格</th>
            <th>平仓价格</th>
            <th>方向</th>
            <th>杠杆</th>
            <th>获利</th>
            <th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in history" :key="record.id">
            <td>{{ record.currentcy }}</td>
            <td>{{ record.open_price }}</td>
            <td>{{ record.close_price }}</td>
            <td>{{ record.side === 'buy' ? '做多' : '做空' }}</td>
            <td>{{ record.lever }}x</td>
            <td :class="getProfitClass(record.profit_percentage)">
              {{ record.profit_percentage?.toFixed(2) }}%
            </td>
            <td>{{ formatDate(record.closed_at) }}</td>
          </tr>
        </tbody>
      </table>
      <button @click="$emit('close')">关闭</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SignalHistory',
  props: {
    show: Boolean,
    title: String
  },
  data() {
    return {
      history: []
    }
  },
  watch: {
    show(newVal) {
      if (newVal && this.title) {
        this.fetchHistory()
      }
    }
  },
  methods: {
    async fetchHistory() {
      try {
        const response = await fetch(`http://localhost:8000/api/signals/${encodeURIComponent(this.title)}/history`)
        this.history = await response.json()
      } catch (error) {
        console.error('Error fetching history:', error)
      }
    },
    getProfitClass(profit) {
      if (!profit) return ''
      return profit > 0 ? 'profit-positive' : 'profit-negative'
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString()
    }
  }
}
</script>

<style scoped>
.history-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

th, td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.profit-positive {
  color: #52c41a;
}

.profit-negative {
  color: #f5222d;
}

button {
  margin-top: 10px;
  padding: 8px 16px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background: #40a9ff;
}
</style> 