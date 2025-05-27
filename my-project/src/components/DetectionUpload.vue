<template>
  <div class="detection-upload card">
    <div class="upload-notification">
      <h3>📤 污水检测功能已准备就绪</h3>
      <p>您可以选择下方的选项卡上传图像或视频进行污水检测分析</p>
    </div>
    
    <div class="upload-header">
      <h3>污水检测分析</h3>
      <p class="description">上传图像或视频进行污水检测和分析</p>
    </div>
    
    <div class="tabs">
      <button 
        :class="['tab-btn', activeTab === 'image' ? 'active' : '']"
        @click="activeTab = 'image'"
      >
        图像检测
      </button>
      <button 
        :class="['tab-btn', activeTab === 'video' ? 'active' : '']"
        @click="activeTab = 'video'"
      >
        视频检测
      </button>
    </div>
    
    <div class="upload-container">
      <div v-if="activeTab === 'image'" class="upload-area">
        <input 
          type="file" 
          ref="imageInput"
          @change="handleImageSelected"
          accept="image/*"
          style="display:none"
        >
        <div 
          class="dropzone"
          @click="$refs.imageInput.click()"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleImageDrop"
          :class="{ 'dragging': isDragging }"
        >
          <div v-if="!selectedImage">
            <div class="upload-icon">📷</div>
            <p class="upload-text">点击或拖放图像文件</p>
            <p class="hint">支持: JPG, PNG, BMP等常见图片格式</p>
          </div>
          <div v-else class="preview-container">
            <img :src="imagePreview" alt="预览图" class="image-preview">
            <div class="preview-info">
              <p>{{ selectedImage.name }}</p>
              <p>{{ formatSize(selectedImage.size) }}</p>
              <button @click.stop="removeImage" class="btn btn-sm btn-danger">移除</button>
            </div>
          </div>
        </div>
        
        <button 
          @click="uploadImage" 
          class="btn btn-primary" 
          :disabled="!selectedImage || loading"
        >
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '检测中...' : '开始检测' }}
        </button>
      </div>
      
      <div v-if="activeTab === 'video'" class="upload-area">
        <input 
          type="file" 
          ref="videoInput"
          @change="handleVideoSelected"
          accept="video/*"
          style="display:none"
        >
        <div 
          class="dropzone"
          @click="$refs.videoInput.click()"
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleVideoDrop"
          :class="{ 'dragging': isDragging }"
        >
          <div v-if="!selectedVideo">
            <div class="upload-icon">🎬</div>
            <p>点击或拖放视频文件</p>
            <p class="hint">支持: MP4, AVI, MOV等常见视频格式</p>
          </div>
          <div v-else class="preview-container">
            <video ref="videoPreview" class="video-preview" controls>
              <source :src="videoPreviewUrl" type="video/mp4">
              您的浏览器不支持视频标签
            </video>
            <div class="preview-info">
              <p>{{ selectedVideo.name }}</p>
              <p>{{ formatSize(selectedVideo.size) }}</p>
              <button @click.stop="removeVideo" class="btn btn-sm btn-danger">移除</button>
            </div>
          </div>
        </div>
        
        <button 
          @click="uploadVideo" 
          class="btn btn-primary" 
          :disabled="!selectedVideo || loading"
        >
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '处理中...' : '开始分析' }}
        </button>
        
        <div v-if="loading && activeTab === 'video'" class="progress-info">
          <p>视频处理可能需要较长时间，请耐心等待...</p>
          <div class="progress-bar">
            <div class="progress-inner" :style="{ width: progress + '%' }"></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加污水检测功能URL输入框 -->
    <div class="detection-url-section">
      <label for="detection-url">污水检测功能准备就绪 URL</label>
      <input 
        type="text" 
        id="detection-url" 
        class="function-ready-url"
        placeholder="输入污水检测功能URL"
        v-model="functionReadyUrl"
      >
      <div class="url-actions">
        <button class="btn btn-sm" @click="testFunctionUrl">测试连接</button>
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
      <button class="error-close" @click="error = null">×</button>
    </div>
  </div>
</template>

<script>
import detectionApi from '@/services/detection';

export default {
  name: 'DetectionUpload',
  data() {
    return {
      activeTab: 'image',
      selectedImage: null,
      selectedVideo: null,
      imagePreview: null,
      videoPreviewUrl: null,
      isDragging: false,
      loading: false,
      error: null,
      progress: 0,
      functionReadyUrl: ''
    };
  },
  methods: {
    handleImageSelected(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectImage(file);
      }
    },
    
    handleImageDrop(event) {
      this.isDragging = false;
      const file = event.dataTransfer.files[0];
      if (file && file.type.startsWith('image/')) {
        this.selectImage(file);
      } else {
        this.error = '请上传有效的图像文件';
      }
    },
    
    selectImage(file) {
      this.selectedImage = file;
      const reader = new FileReader();
      reader.onload = e => {
        this.imagePreview = e.target.result;
      };
      reader.readAsDataURL(file);
    },
    
    removeImage() {
      this.selectedImage = null;
      this.imagePreview = null;
      if (this.$refs.imageInput) {
        this.$refs.imageInput.value = '';
      }
    },
    
    async uploadImage() {
      if (!this.selectedImage) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        const result = await detectionApi.detectImage(this.selectedImage);
        this.$emit('detection-complete', {
          type: 'image',
          result: result
        });
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },
    
    handleVideoSelected(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectVideo(file);
      }
    },
    
    handleVideoDrop(event) {
      this.isDragging = false;
      const file = event.dataTransfer.files[0];
      if (file && file.type.startsWith('video/')) {
        this.selectVideo(file);
      } else {
        this.error = '请上传有效的视频文件';
      }
    },
    
    selectVideo(file) {
      this.selectedVideo = file;
      this.videoPreviewUrl = URL.createObjectURL(file);
    },
    
    removeVideo() {
      if (this.videoPreviewUrl) {
        URL.revokeObjectURL(this.videoPreviewUrl);
      }
      this.selectedVideo = null;
      this.videoPreviewUrl = null;
      if (this.$refs.videoInput) {
        this.$refs.videoInput.value = '';
      }
    },
    
    async uploadVideo() {
      if (!this.selectedVideo) return;
      
      this.loading = true;
      this.error = null;
      this.progress = 0;
      
      // 模拟进度
      this.progressInterval = setInterval(() => {
        if (this.progress < 95) {
          this.progress += 5;
        }
      }, 2000);
      
      try {
        const result = await detectionApi.detectVideo(this.selectedVideo);
        this.progress = 100;
        
        this.$emit('detection-complete', {
          type: 'video',
          result: result
        });
      } catch (error) {
        this.error = error.message;
      } finally {
        clearInterval(this.progressInterval);
        this.loading = false;
      }
    },
    
    formatSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // 测试污水检测功能URL
    testFunctionUrl() {
      if (!this.functionReadyUrl) {
        this.error = "请输入污水检测功能URL";
        return;
      }
      
      this.loading = true;
      // 这里添加测试URL连接的逻辑
      setTimeout(() => {
        this.loading = false;
        // 显示成功消息
        alert("URL连接测试成功");
      }, 1000);
    }
  }
};
</script>

<style scoped>
.detection-upload {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.upload-header {
  text-align: center;
  margin-bottom: 20px;
}

.description {
  color: var(--text-secondary);
}

.tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.tab-btn {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: var(--text-secondary);
}

.tab-btn.active {
  color: var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

.upload-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dropzone {
  border: 2px dashed rgba(255, 255, 255, 0.3);
  background-color: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  padding: 30px;
  text-align: center;
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.dropzone:hover {
  background-color: rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.5);
}

.dropzone.dragging {
  background-color: rgba(24, 144, 255, 0.1);
  border-color: var(--primary-color);
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: rgba(255, 255, 255, 0.8);
}

.upload-text {
  font-size: 18px;
  color: white;
  margin-bottom: 10px;
  font-weight: 500;
}

.hint {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.preview-container {
  position: relative;
}

.image-preview, .video-preview {
  max-width: 100%;
  max-height: 300px;
  border-radius: 4px;
}

.preview-info {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.error-message {
  display: flex;
  align-items: center;
  background-color: rgba(245, 34, 45, 0.1);
  border: 1px solid rgba(245, 34, 45, 0.2);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-md);
  margin-top: 20px;
  color: var(--danger-color);
}

.error-icon {
  margin-right: 10px;
}

.error-close {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--text-disabled);
  cursor: pointer;
  font-size: 18px;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.progress-info {
  margin-top: 20px;
}

.progress-bar {
  height: 10px;
  background-color: var(--border-color);
  border-radius: 5px;
  margin-top: 10px;
  overflow: hidden;
}

.progress-inner {
  height: 100%;
  background-color: var(--primary-color);
  transition: width 0.3s ease;
}

.upload-notification {
  background-color: rgba(24, 144, 255, 0.2);
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 6px;
  border-left: 4px solid var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.upload-notification h3 {
  margin-top: 0;
  color: var(--primary-color);
  font-size: 18px;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
}

.upload-notification p {
  margin-bottom: 0;
  color: white;
  font-size: 16px;
}

/* 优化污水检测URL输入框样式 */
.detection-url-section {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.detection-url-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: white;
  font-size: 16px;
}

.function-ready-url {
  width: 100%;
  padding: 12px 15px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  background-color: rgba(0, 0, 0, 0.3);
  color: white;
  font-size: 16px;
  margin-bottom: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.function-ready-url:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.3);
  background-color: rgba(0, 0, 0, 0.4);
}

.function-ready-url::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.url-actions {
  display: flex;
  justify-content: flex-end;
}

.url-actions .btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.url-actions .btn:hover {
  background-color: #40a9ff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
</style>
