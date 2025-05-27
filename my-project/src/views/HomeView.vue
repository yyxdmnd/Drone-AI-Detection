<template>
  <div class="home-view">
    <h1>无人机污水监测系统</h1>
    <div class="dashboard-summary">
      <p>欢迎使用无人机污水监测系统。请使用上方导航栏访问不同功能。</p>
    </div>
    
    <div class="feature-cards">
      <div class="feature-card" @click="$router.push('/tasks')">
        <div class="card-icon">📋</div>
        <h3>任务管理</h3>
        <p>管理监测任务和计划</p>
      </div>
      
      <div class="feature-card" @click="$router.push('/detection')">
        <div class="card-icon">🔍</div>
        <h3>污水检测</h3>
        <p>上传图像或视频进行污水检测分析</p>
      </div>
    </div>

    <div class="direct-links" style="margin-top: 40px; text-align: center;">
      <h3>直接链接导航</h3>
      <div style="margin-top: 20px; display: flex; justify-content: center; gap: 20px;">
        <button 
          @click="$router.push('/detection')" 
          style="padding: 12px 24px; background: #1890ff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;"
        >
          打开污水检测功能
        </button>
        <button 
          @click="$router.push('/tasks')" 
          style="padding: 12px 24px; background: #52c41a; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;"
        >
          打开任务管理
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
.home-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  margin-bottom: 40px;
  color: var(--primary-color);
}

.dashboard-summary {
  text-align: center;
  margin-bottom: 40px;
}

.feature-cards {
  display: flex;
  gap: 30px;
  justify-content: center;
  flex-wrap: wrap;
}

.feature-card {
  background-color: var(--card-bg, #fff);
  border-radius: 8px;
  padding: 30px;
  width: 250px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.card-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.feature-card h3 {
  margin-bottom: 10px;
  color: var(--primary-color);
}

.feature-card p {
  color: var(--text-secondary, #666);
}
</style>
