<template>
  <div class="statistics-modal" v-if="show">
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
    </div>
    
    <div class="modal-content">
      <h3>策略平仓统计</h3>
      
      <div v-if="error" class="error-message">
        {{ error }}
        <button @click="fetchStatistics">重试</button>
      </div>

      <div class="actions">
        <button @click="exportData" :disabled="!statistics.length">
          导出数据
        </button>
      </div>
      
      <div class="date-picker">
        <input type="datetime-local" v-model="startTime">
        <span>至</span>
        <input type="datetime-local" v-model="endTime">
        <button @click="fetchStatistics">查询</button>
      </div>
      
      <div class="statistics-content" v-if="statistics.length">
        <div class="statistics-summary">
          <h4>总体统计</h4>
          <div class="summary-info">
            <span>策略总数: {{ statistics.length }}</span>
            <span>总平仓次数: {{ getTotalCloseCount() }}</span>
            <span>总盈利次数: {{ getTotalWinCount() }}</span>
            <span>总亏损次数: {{ getTotalLoseCount() }}</span>
            <span :class="getProfitClass(getTotalProfit())">
              总收益率: {{ getTotalProfit()?.toFixed(2) }}%
            </span>
          </div>
        </div>
        
        <div v-for="stat in statistics" :key="stat.title" class="strategy-stat">
          <div class="strategy-header">
            <h4>{{ stat.title }}</h4>
            <div class="strategy-rate">
              胜率: {{ ((stat.win_count / stat.close_count) * 100).toFixed(2) }}%
            </div>
          </div>
          <div class="stat-summary">
            <span>平仓次数: {{ stat.close_count }}</span>
            <span>盈利次数: {{ stat.win_count }}</span>
            <span>亏损次数: {{ stat.lose_count }}</span>
            <span :class="getProfitClass(stat.total_profit)">
              总收益: {{ stat.total_profit?.toFixed(2) }}%
            </span>
          </div>
          <table>
            <thead>
              <tr>
                <th>时间</th>
                <th>交易对</th>
                <th>开仓价</th>
                <th>平仓价</th>
                <th>收益</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in stat.records" :key="index">
                <td>{{ formatDate(record.closed_at) }}</td>
                <td>{{ record.currentcy }}</td>
                <td>{{ record.open_price }}</td>
                <td>{{ record.close_price }}</td>
                <td :class="getProfitClass(record.profit_percentage)">
                  {{ record.profit_percentage?.toFixed(2) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-else class="no-data">
        暂无数据
      </div>
      <button class="close-btn" @click="$emit('close')">关闭</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SignalStatistics',
  props: {
    show: Boolean
  },
  data() {
    return {
      loading: false,
      error: null,
      startTime: '',
      endTime: '',
      statistics: []
    }
  },
  methods: {
    formatDateTime(date) {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day}T${hours}:${minutes}`
    },
    async fetchStatistics() {
      this.loading = true
      this.error = null
      
      try {
        // 将日期转换为完整的 ISO 格式
        const startDate = new Date(this.startTime)
        const endDate = new Date(this.endTime)
        const startIso = startDate.toISOString()
        const endIso = endDate.toISOString()

        console.log('Fetching statistics for:', { startIso, endIso }) // 添加调试日志

        const response = await fetch(
          `http://localhost:8000/api/signals/statistics?start_time=${encodeURIComponent(startIso)}&end_time=${encodeURIComponent(endIso)}`
        )
        if (response.ok) {
          this.statistics = await response.json()
          console.log('Statistics:', this.statistics) // 添加调试日志
        } else {
          const error = await response.text()
          console.error('Error fetching statistics:', error)
        }
      } catch (error) {
        this.error = "获取数据失败，请重试"
        console.error('Error:', error)
      } finally {
        this.loading = false
      }
    },
    getProfitClass(profit) {
      if (!profit) return ''
      return profit > 0 ? 'profit-positive' : 'profit-negative'
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString()
    },
    getTotalCloseCount() {
      return this.statistics.reduce((sum, stat) => sum + stat.close_count, 0)
    },
    getTotalWinCount() {
      return this.statistics.reduce((sum, stat) => sum + stat.win_count, 0)
    },
    getTotalLoseCount() {
      return this.statistics.reduce((sum, stat) => sum + stat.lose_count, 0)
    },
    getTotalProfit() {
      return this.statistics.reduce((sum, stat) => sum + stat.total_profit, 0)
    },
    async exportData() {
      try {
        const csvContent = this.generateCSV()
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = `trading_statistics_${new Date().toISOString()}.csv`
        link.click()
      } catch (error) {
        console.error('Export failed:', error)
      }
    },
    generateCSV() {
      // 生成CSV数据
      const headers = ['策略名称', '平仓次数', '盈利次数', '亏损次数', '总收益']
      const rows = this.statistics.map(stat => [
        stat.title,
        stat.close_count,
        stat.win_count,
        stat.lose_count,
        `${stat.total_profit?.toFixed(2)}%`
      ])
      
      return [headers, ...rows]
        .map(row => row.join(','))
        .join('\n')
    }
  },
  watch: {
    // 添加对 show 属性的监听
    show(newVal) {
      if (newVal) {
        // 当弹窗显示时，设置默认时间范围并获取数据
        const now = new Date()
        const end = new Date(now.getTime() + (24 * 60 * 60 * 1000)) // 往后24小时
        const start = new Date(now.getTime() - (24 * 60 * 60 * 1000)) // 往前24小时
        
        this.endTime = this.formatDateTime(end)
        this.startTime = this.formatDateTime(start)
        
        this.fetchStatistics()
      }
    }
  }
}
</script>

<style scoped>
.statistics-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 1000px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
}

.date-picker {
  margin: 20px 0;
  display: flex;
  gap: 10px;
  align-items: center;
}

.statistics-summary {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.summary-info {
  display: flex;
  gap: 20px;
  margin-top: 10px;
}

.strategy-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.strategy-rate {
  font-size: 14px;
  color: #666;
}

.strategy-stat {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 4px;
  background: white;
}

.stat-summary {
  display: flex;
  gap: 20px;
  margin: 10px 0;
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

.close-btn {
  margin-top: 20px;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #999;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-message {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  padding: 12px;
  margin: 12px 0;
  border-radius: 4px;
  color: #ff4d4f;
}

.actions {
  margin: 12px 0;
  display: flex;
  justify-content: flex-end;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 