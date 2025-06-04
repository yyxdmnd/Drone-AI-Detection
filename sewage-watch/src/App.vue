<script>
import { ref, onMounted, onUnmounted } from 'vue';

export default {
  name: 'DroneDashboard',
  setup() {
    const videoSrc = ref('');
    const fps = ref(0);
    const speed = ref(0);
    const weather = ref('晴朗');
    const leftOpen = ref(false);
    const rightOpen = ref(false);
    const connectionStatus = ref('未连接');
    const showConnectionAlert = ref(false);

    let socket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 9999;   //最大重连尝试次数
    const reconnectDelay = 3000; // 3秒

    const connectWebSocket = () => {
      connectionStatus.value = '连接中';
      socket = new WebSocket('ws://localhost:8000/ws/video');
      
      socket.onopen = () => {
        connectionStatus.value = '已连接';
        showConnectionAlert.value = false;
        reconnectAttempts = 0;
      };
      
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          videoSrc.value = `data:image/jpeg;base64,${data.image}`;
          fps.value = data.fps;
          speed.value = data.speed;
          weather.value = data.weather;
        } catch (e) {
          console.error('解析消息失败:', e);
        }
      };
      
      socket.onclose = (event) => {
        connectionStatus.value = '已断开';
        if (!event.wasClean && reconnectAttempts < maxReconnectAttempts) {
          showConnectionAlert.value = true;
          reconnectAttempts++;
          setTimeout(connectWebSocket, reconnectDelay);
        }
      };
      
      socket.onerror = (error) => {
        console.error('WebSocket错误:', error);
        connectionStatus.value = '连接错误';
      };
    };

    const disconnectWebSocket = () => {
      if (socket) {
        socket.close();
      }
    };

    onMounted(() => {
      connectWebSocket();
    });

    onUnmounted(() => {
      disconnectWebSocket();
    });

    return { 
      videoSrc, 
      fps, 
      speed, 
      weather, 
      leftOpen, 
      rightOpen,
      connectionStatus,
      showConnectionAlert
    };
  }
};
</script>

<template>
  <div id="app">
    <!-- 连接状态提示 -->
    <div v-if="showConnectionAlert" class="connection-alert">
      连接中断，正在尝试重新连接 ({{ reconnectAttempts }}/{{ maxReconnectAttempts }})
    </div>
    
    <!-- 顶部信息栏 -->
    <div class="overlay top-overlay">
      <div class="project-info">
        <h1>无人机污水识别系统</h1>
        <div class="stats">
          <span>帧率: {{ fps }} FPS</span>
          <span>飞行速度: {{ speed }} m/s</span>
          <span>天气: {{ weather }}</span>
        </div>
      </div>
    </div>
    
    <!-- 视频容器 -->
    <div class="video-container">
      <img :src="videoSrc" class="video-bg" id="video-frame" 
           @error="videoSrc = 'fallback-image.jpg'" />
    </div>
    
    <!-- 连接状态指示器 -->
    <div class="connection-status" :class="connectionStatus.toLowerCase()">
      {{ connectionStatus }}
    </div>

    <!-- 底部按钮栏 -->
    <div class="overlay bottom-overlay">
      <div class="btn-group">
        <button class="control-btn">开始任务</button>
        <button class="control-btn">暂停任务</button>
        <button class="control-btn">重置</button>
      </div>
    </div>

    <!-- 左侧任务设置栏 -->
    <div :class="['sidebar', 'left', { open: leftOpen }]">
      <div class="toggle toggle-left overlay" @click="leftOpen = !leftOpen">
        <span>{{ leftOpen ? '◀' : '▶' }}</span>
      </div>
      <div v-if="leftOpen" class="content">
        <h3>任务设置</h3>
      </div>
    </div>

    <!-- 右侧模型设置栏 -->
    <div :class="['sidebar', 'right', { open: rightOpen }]">
      <div class="toggle toggle-right overlay" @click="rightOpen = !rightOpen">
        <span>{{ rightOpen ? '▶' : '◀' }}</span>
      </div>
      <div v-if="rightOpen" class="content">
        <h3>模型设置</h3>
      </div>
    </div>
  </div>

</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron&display=swap');

/* 基础布局 */
#app {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: 'Orbitron', sans-serif;
}

/* 连接状态提示 */
.connection-alert {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 0, 0, 0.7);
  color: white;
  padding: 10px 20px;
  border-radius: 5px;
  z-index: 1000;
  font-size: 0.9rem;
}

/* 连接状态指示器 */
.connection-status {
  position: fixed;
  top: 10px;
  right: 10px;
  padding: 5px 10px;
  border-radius: 3px;
  font-size: 0.8rem;
  z-index: 1000;
}

.connection-status.已连接 {
  background: rgba(0, 255, 0, 0.7);
  color: black;
}

.connection-status.已断开,
.connection-status.连接错误 {
  background: rgba(255, 0, 0, 0.7);
  color: white;
}

.connection-status.连接中 {
  background: rgba(255, 255, 0, 0.7);
  color: black;
}

/* 视频容器 */
.video-container {
  position: fixed;
  top: 100px;    /* 顶部栏高度 */
  bottom: 80px; /* 底部栏高度 */
  left: 0;
  right: 0;
  z-index: 1;
  background-color: #000;
}

.video-bg {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

/* 顶部控制栏 */
.top-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 80px;
  padding: 10px;
  color: #fff;
  z-index: 100;
  backdrop-filter: blur(5px);
  background: linear-gradient(90deg, rgba(0, 102, 204, 0.6), rgba(0, 51, 102, 0.6));
  border-bottom: 1px solid rgba(0, 255, 255, 0.3);
  clip-path: polygon(0 0, 100% 0, 95% 100%, 5% 100%);
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center;     /* 垂直居中 */
}
.project-info {
  text-align: center;
  width: 100%;
}

.project-info h1 {
  margin: 0;
  font-size: 1.8rem;
  color: #00ffff;
  text-shadow: 0 0 10px rgba(0, 255, 255, 0.7);
  display: inline-block; /* 确保文字不换行时也能居中 */
}

.stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 5px;
}

.stats span {
  color: #00ffff;
  font-size: 0.9rem;
}

/* 底部控制栏 */
.bottom-overlay {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  padding: 10px 0;
  z-index: 100;
  backdrop-filter: blur(5px);
  background: linear-gradient(90deg, rgba(0, 102, 204, 0.6), rgba(0, 51, 102, 0.6));
  border-top: 1px solid rgba(0, 255, 255, 0.3);
}

.btn-group {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.control-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  background: rgba(0, 255, 255, 0.2);
  color: #00ffff;
  font-family: 'Orbitron', sans-serif;
  cursor: pointer;
  transition: all 0.3s;
}

.control-btn:hover {
  background: rgba(0, 255, 255, 0.4);
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

/* 侧边栏 */
.sidebar {
  position: fixed;
  top: 80px;    /* 对齐顶部栏 */
  bottom: 60px; /* 对齐底部栏 */
  width: 0;
  background: linear-gradient(180deg, rgba(0,0,50,0.8), rgba(0,0,100,0.8));
  overflow: hidden;
  color: #fff;
  transition: width 0.3s;
  z-index: 200;
}

.sidebar.open {
  width: 250px;
}

.sidebar.left {
  left: 0;
  border-right: 1px solid rgba(0, 255, 255, 0.3);
}

.sidebar.right {
  right: 0;
  border-left: 1px solid rgba(0, 255, 255, 0.3);
}

.toggle {
  position: fixed;
  top: 50%;
  width: 30px;
  height: 60px;
  background: linear-gradient(180deg, rgba(0,255,255,0.6), rgba(0,100,255,0.6));
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 300;
  color: #00ffff;
  font-size: 1.5rem;
  font-weight: bold;
  border: 1px solid rgba(0,255,255,0.6);
  transform: translateY(-50%);
  transition: all 0.3s;
}

.toggle:hover {
  background: linear-gradient(180deg, rgba(0,255,255,0.8), rgba(0,100,255,0.8));
}

.toggle-left {
  left: 0;
}

.sidebar.left.open .toggle-left {
  left: 250px;
}

.toggle-right {
  right: 0;
}

.sidebar.right.open .toggle-right {
  right: 250px;
}

.content {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.content h3 {
  color: #00ffff;
  border-bottom: 1px solid rgba(0, 255, 255, 0.3);
  padding-bottom: 10px;
  margin-top: 0;
}
</style>