<template>
  <div class="detection-view">
    <h2 class="page-title">污水智能检测系统</h2>
    
    <!-- 添加调试信息 -->
    <div class="debug-info">
      <p>调试信息: DetectionView 组件已加载</p>
    </div>
    
    <!-- 添加污水检测功能接口设置 -->
    <div class="detection-api-config">
      <h3 class="section-title">污水检测功能接口设置</h3>
      <div class="api-form">
        <div class="form-group">
          <label for="api-url">功能调用URL</label>
          <input 
            type="text" 
            id="api-url" 
            class="api-input"
            placeholder="输入污水检测API接口地址"
          >
        </div>
        <div class="form-actions">
          <button class="btn btn-primary">保存设置</button>
          <button class="btn btn-secondary">重置</button>
        </div>
      </div>
    </div>
    
    <div v-if="!detectionResult">
      <DetectionUpload @detection-complete="handleDetectionComplete" />
    </div>
    
    <div v-else>
      <DetectionResult 
        :result="detectionResult"
        @close="detectionResult = null"
      />
    </div>

    <div class="view-history-link">
      <router-link to="/detection/history" class="btn btn-secondary">
        查看历史检测记录
      </router-link>
    </div>
  </div>
</template>

<script>
import DetectionUpload from '@/components/DetectionUpload.vue';
import DetectionResult from '@/components/DetectionResult.vue';

export default {
  name: 'DetectionView',
  components: {
    DetectionUpload,
    DetectionResult
  },
  data() {
    return {
      detectionResult: null
    };
  },
  mounted() {
    console.log('DetectionView 组件已挂载');
  },
  methods: {
    handleDetectionComplete(result) {
      console.log('原始检测完成结果:', result);
      
      // 规范化数据结构
      let processedResult = { ...result };
      
      // 确保所有必要的属性都存在
      if (processedResult.type === 'image') {
        // 如果 result 子对象不存在，初始化它
        if (!processedResult.result) {
          processedResult.result = {};
        }
        
        // 确保 detections 数组存在
        if (!processedResult.result.detections) {
          // 如果 detections 在顶层
          if (processedResult.detections) {
            processedResult.result.detections = processedResult.detections;
          } else {
            processedResult.result.detections = [];
          }
        }
        
        console.log('规范化后的检测结果:', processedResult);
        
        // 添加更详细的调试信息
        console.log('图像检测结果:');
        console.log('- 检测对象数:', processedResult.result.detections.length);
        
        // 检查图片数据
        if (processedResult.result.result_image) {
          console.log('- 图片类型:', typeof processedResult.result.result_image);
          console.log('- 图片数据长度:', processedResult.result.result_image.length);
          console.log('- 图片数据开头:', processedResult.result.result_image.substring(0, 30) + '...');
        }
        
        if (processedResult.result.result_image_url) {
          console.log('- 图片URL:', processedResult.result.result_image_url);
        }
        
        // 更新污水判断逻辑，基于polluted置信度
        const pollutedDetection = processedResult.result.detections.find(detection => 
          detection.class_name.toLowerCase() === 'polluted'
        );
        
        const hasWastewater = pollutedDetection && pollutedDetection.confidence > 0.5;
        
        console.log('- 是否检测到污水:', hasWastewater);
        if (pollutedDetection) {
          console.log('- 污水检测置信度:', pollutedDetection.confidence);
        }
        
        processedResult.result.isWastewater = hasWastewater;
      }
      
      // 保存处理后的结果
      this.detectionResult = processedResult;
    }
  }
};
</script>

<style scoped>
.detection-view {
  padding: 20px;
}

.page-title {
  text-align: center;
  margin-bottom: 30px;
  color: white;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  font-weight: 600;
  font-size: 28px;
}

.debug-info {
  background: rgba(0, 0, 0, 0.3);
  padding: 12px 15px;
  margin: 10px 0 20px;
  border-radius: 6px;
  border-left: 4px solid var(--primary-color);
  color: white;
}

.detection-api-config {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.section-title {
  color: white;
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 8px;
}

.api-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: white;
  font-weight: 500;
  font-size: 16px;
}

.api-input {
  width: 100%;
  padding: 12px 15px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  background-color: rgba(0, 0, 0, 0.3);
  color: white;
  font-size: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.api-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.3);
  background-color: rgba(0, 0, 0, 0.4);
}

.api-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 10px;
}

.form-actions .btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  border: none;
}

.form-actions .btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.form-actions .btn-secondary {
  background-color: transparent;
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: white;
}

.form-actions .btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.view-history-link {
  margin-top: 30px;
  text-align: center;
}

.view-history-link .btn {
  padding: 10px 20px;
  background-color: #52c41a;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
}

.view-history-link .btn:hover {
  background-color: #389e0d;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}
</style>
