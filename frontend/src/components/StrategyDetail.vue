<template>
  <div class="strategy-detail">
    <h2>策略详情</h2>
    <div class="strategy-stats">
      <div class="stat-item">
        <h4>总收益率</h4>
        <p :class="{ 'positive': totalProfit > 0, 'negative': totalProfit < 0 }">
          {{ totalProfit.toFixed(2) }}%
        </p>
      </div>
      <div class="stat-item">
        <h4>连续盈利/亏损</h4>
        <p>{{ streakText }}</p>
      </div>
    </div>
    <div class="strategy-image">
      <img :src="strategyImageUrl" v-if="strategyImageUrl">
      <button @click="generateImage">生成晒单图</button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    strategyName: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      signals: [],
      strategyImageUrl: null,
      totalProfit: 0,
      streakText: ''
    }
  },
  async created() {
    await this.fetchStrategyData()
  },
  methods: {
    async fetchStrategyData() {
      try {
        const response = await fetch(`http://localhost:8000/api/signals?strategy=${this.strategyName}`)
        this.signals = await response.json()
        this.calculateStats()
      } catch (error) {
        console.error('Error fetching strategy data:', error)
      }
    },
    calculateStats() {
      // 计算总收益
      this.totalProfit = this.signals.reduce((sum, signal) => {
        return sum + (signal.profit_percentage || 0)
      }, 0)
      
      // 计算连续盈亏
      let streak = 0
      let isPositive = null
      for (const signal of this.signals) {
        if (signal.profit_percentage) {
          const currentIsPositive = signal.profit_percentage > 0
          if (isPositive === null) {
            isPositive = currentIsPositive
            streak = 1
          } else if (isPositive === currentIsPositive) {
            streak++
          } else {
            break
          }
        }
      }
      this.streakText = streak > 0 
        ? `连续${streak}次${isPositive ? '盈利' : '亏损'}`
        : '暂无交易记录'
    },
    async generateImage() {
      try {
        const response = await fetch(`http://localhost:8000/api/signals/${this.strategyName}/image`)
        const blob = await response.blob()
        this.strategyImageUrl = URL.createObjectURL(blob)
      } catch (error) {
        console.error('Error generating strategy image:', error)
      }
    }
  }
}
</script>

<style scoped>
.strategy-detail {
  padding: 20px;
}

.strategy-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-item {
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.positive {
  color: green;
}

.negative {
  color: red;
}

.strategy-image {
  margin-top: 20px;
}

.strategy-image img {
  max-width: 100%;
  margin-bottom: 10px;
}
</style> 