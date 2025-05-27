<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo">
        <img src="/img/logo.png" alt="Logo" class="logo-img" />
        <h1>无人机污水监测系统</h1>
      </div>
      
      <!-- 导航栏 -->
      <nav class="main-nav">
        <router-link to="/" class="nav-item">首页</router-link>
        <router-link to="/tasks" class="nav-item">任务管理</router-link>
        <router-link to="/detection" class="nav-item">污水检测</router-link>
      </nav>
      
      <div class="header-controls">
        <div class="connection-status">
          <span class="status-indicator" :class="{ active: isConnected }"></span>
          {{ isConnected ? '已连接' : '未连接' }}
        </div>
        <button class="settings-btn">
          <i class="settings-icon">⚙️</i>
        </button>
      </div>
    </header>
    
    <!-- 主内容区域 - 只包含router-view，移除其他可能覆盖的内容 -->
    <main class="app-content">
      <router-view />
    </main>
    
    <footer class="app-footer">
      <div class="footer-content">
        <p>© {{ new Date().getFullYear() }} 无人机污水监测系统 - 版本 1.0.0</p>
      </div>
    </footer>
    
    <Toast ref="toast" />
  </div>
</template>

<script>
import Toast from './components/Toast.vue';

export default {
  name: 'App',
  components: {
    Toast
  },
  data() {
    return {
      isConnected: true
    }
  }
}
</script>

<style>
:root {
  --primary-color: #1890ff;
  --secondary-color: #52c41a;
  --danger-color: #f5222d;
  --warning-color: #faad14;
  --dark-bg: #222;
  --darker-bg: #111;
  --light-text: #fff;
  --gray-text: #bbb;
  
  /* 添加缺失的CSS变量 */
  --text-primary: #333;
  --text-secondary: #666;
  --text-disabled: #999;
  --divider-color: #e8e8e8;
  --border-radius-base: 4px;
  --border-radius-large: 8px;
  --card-bg: #fff;
  --card-bg-secondary: #f9f9f9;
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --shadow-base: 0 2px 8px rgba(0, 0, 0, 0.15);
  --shadow-large: 0 4px 16px rgba(0, 0, 0, 0.15);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: var(--darker-bg);
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: var(--dark-bg);
  color: var(--light-text);
  padding: 10px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  align-items: center;
}

.logo-img {
  height: 40px;
  margin-right: 10px;
}

.logo h1 {
  font-size: 1.5rem;
  font-weight: 600;
}

.header-controls {
  display: flex;
  align-items: center;
}

.connection-status {
  display: flex;
  align-items: center;
  margin-right: 20px;
  font-size: 0.9rem;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #777;
  margin-right: 8px;
}

.status-indicator.active {
  background-color: var(--secondary-color);
  box-shadow: 0 0 8px rgba(82, 196, 26, 0.5);
}

.settings-btn {
  background: transparent;
  border: none;
  color: var(--light-text);
  cursor: pointer;
  font-size: 1.2rem;
}

.app-content {
  flex: 1;
  padding: 20px;
}

.app-footer {
  background-color: var(--dark-bg);
  color: var(--gray-text);
  padding: 15px;
  text-align: center;
  font-size: 0.9rem;
}

.main-nav {
  display: flex;
  justify-content: center;
  flex: 1;
}

.nav-item {
  color: var(--light-text);
  text-decoration: none;
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
  border-radius: 4px;
  transition: all 0.3s;
  font-weight: 500;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--primary-color);
}

.router-link-active {
  color: var(--primary-color);
  background-color: rgba(24, 144, 255, 0.1);
}

/* 添加全局表单元素样式 */
select, input, textarea, button {
  font-family: inherit;
  font-size: 14px;
}

select {
  appearance: none;
  background-color: #fff;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%23333' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14L2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 12px;
  padding-right: 2.5rem;
  color: #333;
}

select:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

/* 下拉选项样式 */
select option {
  background-color: white;
  color: #333;
  padding: 8px 12px;
}

/* 修复Firefox特定的选择框样式 */
@-moz-document url-prefix() {
  select {
    text-indent: 0.01px;
    text-overflow: '';
    padding-right: 1em;
  }
}

/* 悬停状态 */
select:hover {
  border-color: #40a9ff;
}

/* 禁用状态 */
select:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

/* 表单元素通用样式 */
.input {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--text-primary);
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid var(--divider-color);
  border-radius: var(--border-radius-base);
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.input:focus {
  border-color: var(--primary-color);
  outline: 0;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

label {
  display: inline-block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-secondary);
}

/* 按钮样式增强 */
.btn {
  display: inline-block;
  font-weight: 500;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  user-select: none;
  border: 1px solid transparent;
  padding: 0.45rem 0.9rem;
  font-size: 1rem;
  line-height: 1.5;
  border-radius: var(--border-radius-base);
  transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, 
              border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  cursor: pointer;
}

.btn:focus, .btn:hover {
  text-decoration: none;
  outline: 0;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

.btn-primary {
  color: #fff;
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.btn-primary:hover {
  background-color: #40a9ff;
  border-color: #40a9ff;
}

.btn-primary:focus {
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.25);
}

/* 卡片样式增强 */
.card {
  background-color: var(--card-bg);
  border-radius: var(--border-radius-base);
  box-shadow: var(--shadow-base);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}
</style> 