<template>
  <div class="detection-result card" v-if="result">
    <div class="result-header">
      <h3>检测结果</h3>
      <button class="btn btn-sm" @click="$emit('close')">返回</button>
    </div>
    
    <div class="result-content">
      <!-- 图像检测结果 -->
      <div v-if="result.type === 'image'" class="image-result">
        <div class="result-image-container">
          <img 
            :src="getResultImageSrc(result.result)" 
            alt="检测结果" 
            class="result-image"
            @error="handleImageError"
          />
        </div>
        
        <div class="detection-details">
          <h4>检测详情</h4>
          
          <!-- 污水检测结果提示 -->
          <div class="wastewater-result">
            <div :class="['alert', hasWastewaterDetection ? 'alert-warning' : 'alert-info']">
              <strong>{{ wastewaterMessage }}</strong>
              <p v-if="hasWastewaterDetection">
                系统检测到污水相关特征，置信度值较高。
                <span v-if="getPollutedConfidence" class="confidence-tag">
                  置信度: {{ getPollutedConfidence }}%
                </span>
              </p>
              <p v-else>系统未检测到明显的污水特征。</p>
            </div>
          </div>
          
          <div class="stats">
            <div class="stat-item">
              <div class="stat-value">{{ result.result.detections.length }}</div>
              <div class="stat-label">检测对象数</div>
            </div>
          </div>
          
          <div class="detections-list" v-if="result.result.detections && result.result.detections.length > 0">
            <div 
              v-for="(detection, index) in result.result.detections" 
              :key="index"
              class="detection-item"
              :class="{'highlight': detection.class_name.toLowerCase() === 'polluted' && detection.confidence > 0.5}"
            >
              <div class="detection-header">
                <div class="detection-class">{{ detection.class_name }}</div>
                <div v-if="detection.class_name.toLowerCase() === 'polluted' && detection.confidence > 0.5" 
                     class="detection-icon">⚠️</div>
              </div>
              <div class="detection-confidence">
                置信度: 
                <span :class="{'high-confidence': detection.class_name.toLowerCase() === 'polluted' && detection.confidence > 0.5}">
                  {{ (detection.confidence * 100).toFixed(2) }}%
                </span>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-detections">
            <p>本次检测未发现任何目标。</p>
          </div>
        </div>
      </div>
      
      <!-- 视频检测结果 -->
      <div v-else-if="result.type === 'video'" class="video-result">
        <div class="result-video-container">
          <video 
            :src="getFullUrl(result.result.result_video_url)" 
            controls 
            class="result-video"
          ></video>
        </div>
        
        <div class="detection-details">
          <h4>检测摘要</h4>
          <div class="stats">
            <div class="stat-item">
              <div class="stat-value">{{ result.result.detections_count }}</div>
              <div class="stat-label">检测对象总数</div>
            </div>
          </div>
          
          <div class="video-info">
            <p>视频处理完成，您可以播放视频查看检测结果。</p>
            <p>检测结果已叠加在视频帧上显示。</p>
          </div>
          
          <div class="download-section">
            <a 
              :href="getFullUrl(result.result.result_video_url)" 
              download
              class="btn btn-primary"
            >
              下载结果视频
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import config from '@/config';

export default {
  name: 'DetectionResult',
  props: {
    result: {
      type: Object,
      required: true
    }
  },
  computed: {
    // 判断是否检测到污水
    hasWastewaterDetection() {
      console.log('计算是否有污水:', this.result);
      
      // 检查结果对象结构
      if (!this.result) return false;
      
      // 先检查是否在顶层有 detections 数组
      let detections = this.result.detections || [];
      
      // 如果在 result 子属性中
      if (this.result.result && this.result.result.detections) {
        detections = this.result.result.detections;
      }
      
      // 如果没有检测结果，肯定不是污水
      if (!detections || detections.length === 0) {
        console.log('没有检测结果');
        return false;
      }
      
      console.log('检测结果数组:', detections);
      
      // 查找 polluted 检测结果并检查置信度
      const pollutedDetection = detections.find(detection => 
        detection.class_name.toLowerCase() === 'polluted'
      );
      
      // 如果找到 polluted 且置信度大于 50%
      if (pollutedDetection && pollutedDetection.confidence > 0.5) {
        console.log('找到污水检测结果，置信度:', pollutedDetection.confidence);
        return true;
      }
      
      console.log('没有找到污水检测结果或置信度不足');
      return false;
    },
    
    // 获取污水检测提示信息
    wastewaterMessage() {
      return this.hasWastewaterDetection 
        ? "经简易污水系统检测，此处检测内容可能含有污水" 
        : "经检测，此处检测内容不含污水";
    },
    
    getPollutedConfidence() {
      if (this.result && this.result.result && this.result.result.detections) {
        const pollutedDetection = this.result.result.detections.find(detection => 
          detection.class_name.toLowerCase() === 'polluted'
        );
        if (pollutedDetection) {
          return (pollutedDetection.confidence * 100).toFixed(2);
        }
      }
      return null;
    }
  },
  methods: {
    getResultImageSrc(resultData) {
      // 处理多种可能的图片格式
      console.log('处理检测结果图片:', resultData);
      
      // 检查是否有Base64格式的图片数据
      if (resultData.result_image && resultData.result_image.length > 200 && !resultData.result_image.startsWith('http') && !resultData.result_image.startsWith('/')) {
        console.log('检测到Base64格式图片');
        return `data:image/jpeg;base64,${resultData.result_image}`;
      }
      
      // 检查是否有URL格式的图片路径
      if (resultData.result_image_url) {
        console.log('检测到图片URL路径');
        return this.getFullUrl(resultData.result_image_url);
      }
      
      // 检查是否有相对路径格式的图片
      if (resultData.result_image && (resultData.result_image.startsWith('/') || resultData.result_image.startsWith('media/'))) {
        console.log('检测到图片相对路径');
        return this.getFullUrl(resultData.result_image);
      }
      
      console.warn('未检测到有效的图片数据', resultData);
      return '/img/no-image.png';
    },
    
    getFullUrl(path) {
      // 确保URL是完整的
      if (path && path.startsWith('/')) {
        // 使用后端基础URL
        return `${config.apiBaseUrl.replace('/api', '')}${path}`;
      }
      return path;
    },
    
    handleImageError(e) {
      console.error('检测结果图片加载失败:', e.target.src);
      e.target.src = '/img/no-image.png';
      e.target.style.border = '1px dashed #ccc';
      e.target.style.padding = '10px';
    }
  }
};
</script>

<style scoped>
.detection-result {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.image-result, .video-result {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

@media (min-width: 768px) {
  .image-result, .video-result {
    flex-direction: row;
    align-items: flex-start;
  }
  
  .result-image-container, .result-video-container {
    flex: 2;
  }
  
  .detection-details {
    flex: 1;
  }
}

.result-image-container, .result-video-container {
  background-color: #000;
  border-radius: 8px;
  overflow: hidden;
  text-align: center;
}

.result-image, .result-video {
  max-width: 100%;
  max-height: 500px;
}

.detection-details {
  background-color: var(--card-bg-secondary);
  border-radius: 8px;
  padding: 15px;
}

.stats {
  display: flex;
  gap: 20px;
  margin: 15px 0;
}

.stat-item {
  background-color: var(--card-bg);
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--primary-color);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 5px;
}

.detections-list {
  margin-top: 20px;
  max-height: 300px;
  overflow-y: auto;
}

.detection-item {
  background-color: var(--card-bg);
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 10px;
  border-left: 3px solid var(--primary-color);
}

.detection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detection-class {
  font-weight: bold;
}

.detection-confidence {
  font-size: 14px;
  color: var(--text-secondary);
}

.video-info {
  margin: 15px 0;
  padding: 10px;
  background-color: rgba(var(--primary-rgb), 0.1);
  border-radius: 6px;
}

.download-section {
  margin-top: 20px;
  text-align: center;
}

.wastewater-result {
  margin: 20px 0;
}

.alert {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.alert-warning {
  background-color: #f5222d11;
  border: 2px solid #f5222d;
  color: #cf1322;
  position: relative;
  padding-left: 45px;
}

.alert-warning::before {
  content: "⚠️";
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 20px;
}

.alert-warning strong {
  color: #cf1322;
  font-size: 18px;
  font-weight: 600;
}

.alert-warning p {
  color: #434343;
  font-weight: 500;
}

.alert-info {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
  color: #1890ff;
  position: relative;
  padding-left: 45px;
}

.alert-info::before {
  content: "✓";
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24px;
  font-weight: bold;
  color: #52c41a;
}

.alert-info strong {
  display: block;
  color: #1890ff;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
}

.alert-info p {
  color: #434343;
  font-weight: 500;
}

.empty-detections {
  padding: 15px;
  text-align: center;
  color: #999;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-top: 15px;
}

.detection-item.highlight {
  background-color: rgba(245, 34, 45, 0.05);
  border-left: 3px solid #f5222d;
  position: relative;
  font-weight: 500;
}

.detection-item.highlight .detection-class,
.detection-item.highlight .detection-confidence {
  color: #cf1322;
}

.confidence-tag {
  display: inline-block;
  background-color: #cf1322;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  margin-left: 8px;
}

.detection-icon {
  color: #cf1322;
  font-size: 18px;
  margin-left: 5px;
}

.high-confidence {
  font-weight: bold;
}
</style>
