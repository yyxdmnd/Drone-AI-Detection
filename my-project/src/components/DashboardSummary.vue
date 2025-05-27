<template>
  <div class="dashboard-summary card">
    <h2 class="dashboard-title">系统概览</h2>
    
    <div class="metrics-grid">
      <!-- 无人机状态 -->
      <div class="metric-card" :class="{ 'alert': !droneConnected }">
        <div class="metric-icon">🛸</div>
        <div class="metric-content">
          <div class="metric-title">无人机状态</div>
          <div class="metric-value">{{ droneConnected ? '已连接' : '未连接' }}</div>
          <div class="metric-sub">{{ droneLastSeen }}</div>
        </div>
      </div>
      
      <!-- 电池电量 -->
      <div class="metric-card" :class="{ 'warning': batteryLevel < 30, 'alert': batteryLevel < 15 }">
        <div class="metric-icon">🔋</div>
        <div class="metric-content">
          <div class="metric-title">电池电量</div>
          <div class="metric-value">{{ batteryLevel }}%</div>
          <div class="metric-progress">
            <div class="progress-bar" :style="{ width: batteryLevel + '%', backgroundColor: batteryColor }"></div>
          </div>
        </div>
      </div>
      
      <!-- 当前任务 -->
      <div class="metric-card">
        <div class="metric-icon">📋</div>
        <div class="metric-content">
          <div class="metric-title">当前任务</div>
          <div class="metric-value">{{ currentTask || '无进行中的任务' }}</div>
          <div class="metric-sub" v-if="currentTask">开始于: {{ taskStartTime }}</div>
        </div>
      </div>
      
      <!-- 检测结果 -->
      <div class="metric-card" :class="{ 'warning': detectionCount > 3, 'alert': detectionCount > 5 }">
        <div class="metric-icon">🔍</div>
        <div class="metric-content">
          <div class="metric-title">污水检测</div>
          <div class="metric-value">{{ detectionCount }}处</div>
          <div class="metric-sub">最近更新: {{ lastDetectionTime }}</div>
        </div>
      </div>
    </div>
    
    <div class="summary-actions">
      <button class="btn btn-primary" @click="startNewMission">开始新任务</button>
      <button class="btn btn-danger" v-if="droneConnected" @click="emergencyReturn">紧急返航</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardSummary',
  data() {
    return {
      droneConnected: true,
      droneLastSeen: '2分钟前',
      batteryLevel: 78,
      currentTask: '南湖水域巡检',
      taskStartTime: '10:30:45',
      detectionCount: 2,
      lastDetectionTime: '11:45:20'
    };
  },
  computed: {
    batteryColor() {
      if (this.batteryLevel > 50) return 'var(--success-color)';
      if (this.batteryLevel > 20) return 'var(--warning-color)';
      return 'var(--danger-color)';
    }
  },
  methods: {
    startNewMission() {
      this.$emit('start-mission');
    },
    emergencyReturn() {
      if (confirm('确定要执行紧急返航吗？这将中断当前任务。')) {
        this.$emit('emergency-return');
      }
    }
  }
};
</script>

<style scoped>
.dashboard-summary {
  background-color: var(--card-bg);
  border-radius: var(--border-radius-large);
}

.dashboard-title {
  margin-bottom: var(--spacing-lg);
  color: var(--text-primary);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.metric-card {
  display: flex;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-md);
  transition: all 0.3s;
}

.metric-card:hover {
  background-color: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
}

.metric-card.warning {
  border-left: 3px solid var(--warning-color);
}

.metric-card.alert {
  border-left: 3px solid var(--danger-color);
}

.metric-icon {
  font-size: 28px;
  margin-right: var(--spacing-md);
  opacity: 0.8;
}

.metric-content {
  flex: 1;
}

.metric-title {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.metric-value {
  font-size: 20px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.metric-sub {
  font-size: 12px;
  color: var(--text-disabled);
}

.metric-progress {
  height: 6px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  margin-top: 6px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.summary-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}
</style>
