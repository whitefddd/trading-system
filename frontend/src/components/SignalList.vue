<template>
  <div class="signal-list">
    <h2>策略监控面板</h2>
    <div class="statistics">
      <div class="stat-header">
        <div class="stat-card">
          <h3>总策略数</h3>
          <div class="stat-number">{{ signals.length }}</div>
        </div>
        <button class="stat-btn" @click="showStatisticsModal = true">
          查看平仓统计
        </button>
      </div>
    </div>
    <div class="signals-table">
      <table>
        <thead>
          <tr>
            <th>策略名称</th>
            <th>交易对</th>
            <th>实时价格</th>
            <th>开仓价格</th>
            <th>止损价</th>
            <th>止盈价</th>
            <th>杠杆</th>
            <th>方向</th>
            <th>状态</th>
            <th>平仓价格</th>
            <th>连胜/连亏</th>
            <th>获利</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="signal in signals" :key="signal.trade_id">
            <td>{{ signal.title }}</td>
            <td>{{ signal.fullSymbol }}</td>
            <td class="highlight">{{ realTimePrices[signal.fullSymbol] || '-' }}</td>
            <td>{{ signal.open_price || '-' }}</td>
            <td>{{ signal.zs_tp_trigger_px }}</td>
            <td>{{ signal.zy_tp_trigger_px?.join(', ') || '-' }}</td>
            <td>{{ signal.lever }}x</td>
            <td>{{ signal.side === 'buy' ? '做多' : '做空' }}</td>
            <td>{{ signal.is_close === true ? '已平仓' : '持仓中' }}</td>
            <td class="highlight">
              {{ signal.close_price || '-' }}
            </td>
            <td>
              <span :class="getStreakClass(signal)">
                {{ getStreakText(signal) }}
              </span>
            </td>
            <td :class="getProfitClass(signal.profit_percentage)">
              {{ signal.profit_percentage ? signal.profit_percentage.toFixed(2) + '%' : '-' }}
            </td>
            <td>
              <button @click="showHistory(signal.title)">历史记录</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <SignalHistory 
      :show="showHistoryModal"
      :title="selectedTitle"
      @close="showHistoryModal = false"
    />
    <SignalStatistics
      :show="showStatisticsModal"
      @close="showStatisticsModal = false"
    />
  </div>
</template>

<script>
import SignalHistory from './SignalHistory.vue'
import SignalStatistics from './SignalStatistics.vue'

export default {
  name: 'SignalList',
  components: {
    SignalHistory,
    SignalStatistics
  },
  data() {
    return {
      signals: [],
      realTimePrices: {},
      wsConnections: {},
      refreshInterval: null,
      showHistoryModal: false,
      selectedTitle: '',
      showStatisticsModal: false
    }
  },
  async created() {
    await this.fetchSignals()
    this.refreshInterval = setInterval(async () => {
      await this.fetchSignals()
      this.ensureWebSocketConnections()
    }, 1000)
  },
  methods: {
    async fetchSignals() {
      try {
        const response = await fetch('http://localhost:8000/api/signals')
        const data = await response.json()
        console.log('Latest signals:', data)
        
        this.signals = data.map(signal => ({
          ...signal,
          is_close: Boolean(signal.is_close),
          trade_id: signal.trade_id,
          title: signal.title,
          currentcy: signal.currentcy,
          fullSymbol: signal.currentcy ? 
            (signal.currentcy.replace('USDT', '') + 'USDT') : '-',
          close_price: signal.close_price || '-',
          open_price: signal.open_price || '-',
          profit_percentage: signal.profit_percentage || null,
          win_streak: signal.win_streak || 0,
          lose_streak: signal.lose_streak || 0
        }))
        
        console.log('Processed signals:', this.signals)
        
        if (!Object.keys(this.wsConnections).length) {
          this.setupWebSockets()
        }
      } catch (error) {
        console.error('Error fetching signals:', error)
      }
    },
    setupWebSockets() {
      const currencies = [...new Set(this.signals.map(s => s.fullSymbol))]
      
      currencies.forEach(currency => {
        this.setupSingleWebSocket(currency)
      })
    },
    setupSingleWebSocket(currency) {
      if (this.wsConnections[currency]?.readyState === WebSocket.OPEN) return

      const ws = new WebSocket(`ws://localhost:8000/api/ws/${currency.toLowerCase()}`)
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.symbol === currency) {
          this.realTimePrices[currency] = data.price
        }
      }
      
      ws.onclose = () => {
        delete this.wsConnections[currency]
      }
      
      this.wsConnections[currency] = ws
    },
    ensureWebSocketConnections() {
      const currencies = [...new Set(this.signals.map(s => s.fullSymbol))]
      currencies.forEach(currency => {
        if (!this.wsConnections[currency] || this.wsConnections[currency].readyState !== WebSocket.OPEN) {
          this.setupSingleWebSocket(currency)
        }
      })
    },
    getStreakClass(signal) {
      if (signal.win_streak > 0) return 'streak-win'
      if (signal.lose_streak > 0) return 'streak-lose'
      return ''
    },
    getStreakText(signal) {
      if (signal.win_streak > 0) return `连胜${signal.win_streak}`
      if (signal.lose_streak > 0) return `连亏${signal.lose_streak}`
      return '-'
    },
    getProfitClass(profit) {
      if (!profit) return ''
      return profit > 0 ? 'profit-positive' : 'profit-negative'
    },
    showHistory(title) {
      this.selectedTitle = title
      this.showHistoryModal = true
    }
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
    Object.values(this.wsConnections).forEach(ws => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    })
  }
}
</script>

<style scoped>
.signal-list {
  padding: 20px;
}

.statistics {
  margin-bottom: 20px;
}

.stat-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.stat-card {
  background: #f0f2f5;
  padding: 15px;
  border-radius: 8px;
  margin-right: 20px;
  min-width: 150px;
}

.signals-table table {
  width: 100%;
  border-collapse: collapse;
}

.signals-table th,
.signals-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.signals-table th {
  background-color: #f5f5f5;
}

.highlight {
  color: #1890ff;
  font-weight: bold;
}

.streak-win {
  color: #52c41a;
  font-weight: bold;
}

.streak-lose {
  color: #f5222d;
  font-weight: bold;
}

.profit-positive {
  color: #52c41a;
  font-weight: bold;
}

.profit-negative {
  color: #f5222d;
  font-weight: bold;
}

.stat-btn {
  margin-left: 20px;
  padding: 8px 16px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  height: fit-content;
}

.stat-btn:hover {
  background: #40a9ff;
}
</style> 