<template>
  <div class="dashboard">
    <div class="charts-container">
      <ProfitChart :data="profitData" />
      <StrategyPerformance :data="performanceData" />
      <RiskMetrics :data="riskData" />
    </div>
    
    <div class="controls">
      <RiskControls @update="updateRiskParams" />
      <BacktestPanel @run="runBacktest" />
      <NotificationCenter :messages="notifications" />
    </div>
  </div>
</template> 