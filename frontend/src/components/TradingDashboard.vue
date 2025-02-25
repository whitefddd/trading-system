<template>
  <div class="dashboard">
    <div class="strategy-board">
      <h2>策略监控面板</h2>
      <div class="stats">
        <div class="stat-item">
          <label>总策略数</label>
          <div class="value">{{ signals.length }}</div>
        </div>
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
          </tr>
        </thead>
        <tbody>
          <tr v-for="signal in signals" :key="signal.id">
            <td>{{ signal.title }}</td>
            <td>{{ signal.currentcy }}USDT</td>
            <td>{{ prices[signal.currentcy + 'USDT'] || '-' }}</td>
            <td>{{ signal.open_price || '-' }}</td>
            <td>{{ signal.zs_tp_trigger_px || '-' }}</td>
            <td>{{ signal.zy_tp_trigger_px || '-' }}</td>
            <td>{{ signal.lever }}x</td>
            <td>{{ signal.side === 'buy' ? '做多' : '做空' }}</td>
            <td>{{ signal.is_close ? '已平仓' : '持仓中' }}</td>
            <td>{{ signal.close_price || '-' }}</td>
            <td>{{ signal.win_streak }}/{{ signal.lose_streak }}</td>
            <td>{{ signal.is_close ? (signal.profit_percentage * 100).toFixed(2) + '%' : '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="buttons">
      <button @click="viewHistory">查看历史记录</button>
      <button @click="viewClosedStrategies">策略平仓统计</button>
    </div>
  </div>
</template>

<script>
import { webSocketService } from '../services/websocket.js';

export default {
  data() {
    return {
      prices: {},
      signals: []
    };
  },
  
  mounted() {
    this.connectWebSocket();
    this.fetchSignals();
    this.timer = setInterval(this.fetchSignals, 5000);
  },
  
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer);
    }
    webSocketService.unsubscribe(this.handlePriceUpdate);
    webSocketService.disconnect();
  },
  
  methods: {
    connectWebSocket() {
      webSocketService.connect();
      webSocketService.subscribe(this.handlePriceUpdate);
    },
    
    handlePriceUpdate(data) {
      if (data.s && data.p) {
        const symbol = data.s;
        const price = parseFloat(data.p);
        this.$set(this.prices, symbol, price);
      }
    },
    
    async fetchSignals() {
      try {
        const response = await fetch('/api/signals', {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          credentials: 'same-origin'
        });
        if (response.ok) {
          const data = await response.json();
          this.signals = data;
        }
      } catch (error) {
        console.error('Error fetching signals:', error);
      }
    },

    viewHistory() {
      // 实现查看历史记录的逻辑
      console.log('查看历史记录');
    },

    viewClosedStrategies() {
      // 实现查看平仓统计的逻辑
      console.log('查看平仓统计');
    }
  }
};
</script>