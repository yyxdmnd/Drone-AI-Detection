<template>
  <div class="video-monitor">
    <div class="video-container">
      <!-- 视频标题和状态信息 -->
      <div class="video-header">
        <div class="video-title">
          <i class="video-icon">📹</i>
          <span>实时监控画面</span>
        </div>
        <div class="video-status">
          <span class="status-indicator" :class="{ active: isStreaming }"></span>
          {{ isStreaming ? '直播中' : '未连接' }}
        </div>
      </div>
      
      <!-- 视频显示区域 -->
      <div class="video-screen">
        <video ref="video" autoplay muted @canplay="handleCanPlay"></video>
        
        <!-- 检测框覆盖层 -->
        <canvas ref="canvas" class="detection-canvas"></canvas>
        
        <!-- 视频控制器 -->
        <div class="video-controls">
          <button @click="togglePlay" class="control-btn">
            <i>{{ isPlaying ? '⏸' : '▶' }}</i>
          </button>
          <button @click="toggleMute" class="control-btn">
            <i>{{ isMuted ? '🔇' : '🔊' }}</i>
          </button>
          <button @click="toggleFullscreen" class="control-btn">
            <i>🔍</i>
          </button>
          <div class="zoom-controls">
            <button @click="zoomIn" class="control-btn">+</button>
            <button @click="zoomOut" class="control-btn">-</button>
          </div>
        </div>
      </div>
      
      <!-- 检测信息 -->
      <div class="detection-info" v-if="Object.keys(detectionResults).length > 0">
        <div class="info-header">检测结果</div>
        <div v-for="(value, key) in detectionResults" :key="key" class="info-item">
          <span class="info-label">{{ key }}:</span>
          <span class="info-value">{{ value }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VideoMonitor',
  props: {
    videoSource: {
      type: String,
      default: '/videos/sample.mp4'
    },
    detectionResults: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      isStreaming: false,
      isPlaying: false,
      isMuted: true,
      zoomLevel: 1,
      detections: []
    };
  },
  mounted() {
    this.initVideo();
    window.addEventListener('resize', this.resizeCanvas);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.resizeCanvas);
  },
  methods: {
    initVideo() {
      const videoElement = this.$refs.video;
      videoElement.src = this.videoSource;
      videoElement.muted = this.isMuted;
      
      // 模拟检测结果
      this.simulateDetections();
    },
    
    handleCanPlay() {
      this.isStreaming = true;
      this.isPlaying = true;
      this.resizeCanvas();
    },
    
    resizeCanvas() {
      const video = this.$refs.video;
      const canvas = this.$refs.canvas;
      
      if (!video || !canvas) return;
      
      canvas.width = video.clientWidth;
      canvas.height = video.clientHeight;
      
      // 重新绘制检测框
      this.drawDetections();
    },
    
    drawDetections() {
      const canvas = this.$refs.canvas;
      if (!canvas) return;
      
      const context = canvas.getContext('2d');
      context.clearRect(0, 0, canvas.width, canvas.height);
      
      // 绘制检测框
      this.detections.forEach(detection => {
        const { x, y, width, height, label, confidence } = detection;
        
        // 转换为画布坐标
        const canvasX = (x / 100) * canvas.width;
        const canvasY = (y / 100) * canvas.height;
        const canvasWidth = (width / 100) * canvas.width;
        const canvasHeight = (height / 100) * canvas.height;
        
        // 绘制框
        context.beginPath();
        context.rect(canvasX, canvasY, canvasWidth, canvasHeight);
        context.lineWidth = 3;
        context.strokeStyle = 'rgba(255, 0, 0, 0.8)';
        context.stroke();
        
        // 绘制标签背景
        context.fillStyle = 'rgba(255, 0, 0, 0.7)';
        const labelText = `${label} ${Math.round(confidence * 100)}%`;
        const textWidth = context.measureText(labelText).width + 10;
        context.fillRect(canvasX, canvasY - 25, textWidth, 25);
        
        // 绘制标签文字
        context.fillStyle = 'white';
        context.font = '16px Arial';
        context.fillText(labelText, canvasX + 5, canvasY - 7);
      });
    },
    
    simulateDetections() {
      // 模拟检测数据
      this.detections = [
        { x: 20, y: 30, width: 15, height: 12, label: '污水', confidence: 0.92 },
        { x: 60, y: 45, width: 20, height: 15, label: '污水', confidence: 0.87 }
      ];
      
      setTimeout(() => {
        this.drawDetections();
      }, 1000);
    },
    
    togglePlay() {
      const video = this.$refs.video;
      if (this.isPlaying) {
        video.pause();
      } else {
        video.play();
      }
      this.isPlaying = !this.isPlaying;
    },
    
    toggleMute() {
      const video = this.$refs.video;
      video.muted = !video.muted;
      this.isMuted = video.muted;
    },
    
    toggleFullscreen() {
      const videoContainer = this.$el.querySelector('.video-screen');
      
      if (!document.fullscreenElement) {
        videoContainer.requestFullscreen().catch(err => {
          console.error(`全屏请求失败: ${err.message}`);
        });
      } else {
        document.exitFullscreen();
      }
    },
    
    zoomIn() {
      if (this.zoomLevel < 2) {
        this.zoomLevel += 0.1;
        this.applyZoom();
      }
    },
    
    zoomOut() {
      if (this.zoomLevel > 0.5) {
        this.zoomLevel -= 0.1;
        this.applyZoom();
      }
    },
    
    applyZoom() {
      const video = this.$refs.video;
      video.style.transform = `scale(${this.zoomLevel})`;
    }
  }
};
</script>

<style scoped>
.video-monitor {
  background-color: #222;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-bottom: 20px;
}

.video-container {
  position: relative;
}

.video-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #333;
  color: white;
}

.video-title {
  display: flex;
  align-items: center;
  font-weight: bold;
}

.video-icon {
  margin-right: 8px;
}

.video-status {
  display: flex;
  align-items: center;
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
  background-color: #52c41a;
  box-shadow: 0 0 8px rgba(82, 196, 26, 0.5);
}

.video-screen {
  position: relative;
  width: 100%;
  background-color: #000;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.video-screen video {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.detection-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.video-controls {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 10px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.video-screen:hover .video-controls {
  opacity: 1;
}

.control-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  border-radius: 4px;
  width: 36px;
  height: 36px;
  margin-right: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.zoom-controls {
  margin-left: auto;
  display: flex;
}

.detection-info {
  padding: 12px 16px;
  background-color: #333;
  color: white;
  font-size: 0.9rem;
}

.info-header {
  font-weight: bold;
  margin-bottom: 8px;
  color: #1890ff;
}

.info-item {
  display: flex;
  margin-bottom: 4px;
}

.info-label {
  width: 100px;
  color: #999;
}

.info-value {
  font-weight: 500;
}
</style>
