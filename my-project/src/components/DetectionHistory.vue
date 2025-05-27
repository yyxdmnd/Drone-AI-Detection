<template>
  <div class="detection-history card">
    <h3 class="history-title">检测历史记录</h3>
    
    <div class="filters">
      <div class="filter-item">
        <label>检测类别:</label>
        <select v-model="filters.className">
          <option value="">全部</option>
          <option v-for="className in classOptions" :key="className" :value="className">
            {{ className }}
          </option>
        </select>
      </div>
      
      <div class="filter-item">
        <label>开始日期:</label>
        <input type="date" v-model="filters.startDate">
      </div>
      
      <div class="filter-item">
        <label>结束日期:</label>
        <input type="date" v-model="filters.endDate">
      </div>
      
      <button class="btn btn-primary" @click="fetchHistory">查询</button>
      
      <!-- 开发辅助工具 -->
      <div v-if="isDevelopment" class="dev-tools">
        <label class="mock-data-toggle">
          <input type="checkbox" v-model="useMockData" @change="fetchHistory">
          使用模拟数据
        </label>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      加载历史数据中...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else-if="historyData.length === 0" class="empty-history">
      暂无检测历史记录
    </div>
    
    <div v-else class="history-list">
      <div v-for="item in historyData" :key="item.id" class="history-item">
        <div class="history-item-header">
          <div class="history-date">{{ formatDate(item.uploaded_at) }}</div>
          <div class="detection-count">
            检测到 {{ item.detection_results ? item.detection_results.length : 0 }} 个目标
          </div>
        </div>
        
        <div class="history-content">
          <div class="history-image">
            <img :src="getImageUrl(item.result_image)" alt="检测结果" @error="handleImageError">
            <div v-if="item.result_image_loading" class="image-loading">
              加载中...
            </div>
          </div>
          
          <div class="detection-details">
            <h4>检测详情</h4>
            <div class="detection-list">
              <div v-if="!item.detection_results || item.detection_results.length === 0" class="no-results">
                无检测结果数据
              </div>
              <div v-else v-for="(result, index) in item.detection_results" 
                   :key="index" 
                   class="detection-item">
                <div class="detection-class">{{ result.class_name }}</div>
                <div class="detection-confidence">
                  置信度: {{ (result.confidence * 100).toFixed(2) }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="pagination" v-if="historyData.length > 0">
      <button 
        :disabled="currentPage === 1" 
        @click="changePage(currentPage - 1)" 
        class="btn"
      >
        上一页
      </button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button 
        :disabled="currentPage === totalPages" 
        @click="changePage(currentPage + 1)" 
        class="btn"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import config from '@/config';

export default {
  name: 'DetectionHistory',
  data() {
    return {
      historyData: [],
      loading: false,
      error: null,
      currentPage: 1,
      totalCount: 0,
      totalPages: 1,
      classOptions: [],
      filters: {
        className: '',
        startDate: '',
        endDate: ''
      },
      useMockData: false, // 是否使用模拟数据
      isDevelopment: false // 默认为非开发环境
    };
  },
  mounted() {
    // 在组件挂载后设置环境
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.fetchHistory();
    this.fetchClassOptions();
  },
  methods: {
    // 生成模拟数据用于测试
    generateMockData() {
      const mockData = [];
      
      for (let i = 1; i <= 10; i++) {
        mockData.push({
          id: i,
          uploaded_at: new Date(Date.now() - i * 86400000).toISOString(), // 每天一条记录
          result_image: '/img/no-image.png',
          detection_results: Array(Math.floor(Math.random() * 5) + 1).fill(0).map((_, index) => ({
            id: index,
            class_name: this.classOptions[Math.floor(Math.random() * this.classOptions.length)],
            confidence: Math.random() * 0.5 + 0.5, // 0.5 - 1.0之间
            bbox: [Math.random() * 100, Math.random() * 100, Math.random() * 200, Math.random() * 200]
          }))
        });
      }
      
      return mockData;
    },
  
    async fetchHistory() {
      this.loading = true;
      this.error = null;
      
      // 如果启用了模拟数据，直接使用模拟数据
      if (this.useMockData) {
        console.log('使用模拟数据');
        setTimeout(() => {
          const mockData = this.generateMockData();
          this.historyData = mockData;
          this.totalCount = 30; // 假设有30条记录
          this.totalPages = 3;
          this.loading = false;
        }, 500); // 模拟加载延迟
        return;
      }
      
      try {
        let url = `${config.apiBaseUrl}/detection/history/?page=${this.currentPage}`;
        
        // 添加筛选条件
        if (this.filters.className) {
          url += `&class_name=${this.filters.className}`;
        }
        
        if (this.filters.startDate) {
          url += `&start_date=${this.filters.startDate}`;
        }
        
        if (this.filters.endDate) {
          url += `&end_date=${this.filters.endDate}`;
        }
        
        console.log('请求URL:', url);
        const response = await axios.get(url);
        
        // 添加调试输出
        console.log('API 响应状态:', response.status);
        console.log('API 响应数据类型:', typeof response.data);
        console.log('API 响应数据结构:', response.data);
        
        // 检查响应数据格式并相应处理
        let responseData = [];
        let count = 0;
        
        if (Array.isArray(response.data)) {
          // 如果响应直接是一个数组
          console.log('处理数组格式响应');
          responseData = response.data;
          count = response.data.length;
        } else if (response.data && response.data.results) {
          // 如果响应是带有results属性的对象
          console.log('处理分页对象格式响应');
          responseData = response.data.results;
          count = response.data.count || responseData.length;
        } else if (response.data && typeof response.data === 'object') {
          // 如果响应是普通对象，尝试转换为数组
          console.log('处理普通对象格式响应');
          responseData = [response.data];
          count = 1;
        } else {
          // 不支持的格式，设为空数组
          console.log('未识别的响应格式，使用空数组');
          responseData = [];
          count = 0;
        }
        
        // 规范化数据
        if (responseData.length > 0) {
          console.log('样例记录:', responseData[0]);
        }
        
        this.historyData = responseData.map(item => {
          // 确保所有必要的字段都存在
          return {
            ...item,
            id: item.id || Math.random().toString(36).substr(2, 9),
            uploaded_at: item.uploaded_at || new Date().toISOString(),
            result_image: item.result_image || '',
            detection_results: item.detection_results || [],
            result_image_loading: false // 默认图片不在加载状态
          };
        });
        
        this.totalCount = count;
        this.totalPages = Math.ceil(this.totalCount / 10); // 假设每页10条
        
        console.log('处理后的数据:', this.historyData);
      } catch (error) {
        console.error('获取检测历史失败:', error);
        if (error.response) {
          console.error('错误响应:', error.response.status, error.response.data);
          this.error = `获取历史数据失败: ${error.response.status} - ${JSON.stringify(error.response.data)}`;
        } else if (error.request) {
          console.error('请求未响应');
          this.error = '服务器未响应，请检查网络连接';
        } else {
          console.error('请求配置错误:', error.message);
          this.error = `请求错误: ${error.message}`;
        }
      } finally {
        this.loading = false;
      }
    },
    
    async fetchClassOptions() {
      try {
        // 这里可以添加获取所有检测类别的API调用
        // 为简单起见，可以硬编码一些常见类别
        this.classOptions = ['污水', '油污', '垃圾', '藻类'];
      } catch (error) {
        console.error('获取检测类别失败:', error);
      }
    },
    
    changePage(page) {
      this.currentPage = page;
      this.fetchHistory();
    },
    
    getImageUrl(path) {
      // 处理 Base64 格式的图像数据
      if (path && path.startsWith('data:image')) {
        return path; // 已经是完整的数据URL
      }
      
      if (path && path.length > 200 && path.match(/^[A-Za-z0-9+/=]+$/)) {
        // 看起来是Base64编码的图像数据，但缺少前缀
        return `data:image/jpeg;base64,${path}`;
      }

      if (!path) return '/img/no-image.png'; // 返回默认图片路径
      
      // 处理URL路径
      try {
        if (path.startsWith('http')) {
          return path;
        } else if (path.startsWith('/')) {
          return `${config.apiBaseUrl.replace('/api', '')}${path}`;
        } else {
          return `${config.apiBaseUrl.replace('/api', '')}/${path}`;
        }
      } catch (error) {
        console.error('图片URL处理错误:', error, path);
        return '/img/no-image.png'; // 出错时返回默认图片
      }
    },
    
    handleImageError(e) {
      console.log('图片加载失败:', e.target.src);
      
      // 在控制台中也显示详细的错误原因，帮助调试
      if (e.target.src.startsWith('data:image')) {
        console.log('Base64图片加载失败，可能是格式错误或数据损坏');
      } else if (e.target.src.includes('api')) {
        console.log('API返回的图片路径无法加载，检查后端路径是否正确');
      }
      
      // 设置合适的默认图片
      e.target.src = '/img/no-image.png';
      e.target.style.maxWidth = '100%';
      e.target.style.height = 'auto';
      e.target.style.border = '1px dashed #ccc';
      e.target.style.padding = '10px';
      
      // 在图片下方显示错误提示
      const parent = e.target.parentNode;
      if (parent) {
        const errorMsg = document.createElement('div');
        errorMsg.textContent = '图片加载失败';
        errorMsg.style.color = '#f56c6c';
        errorMsg.style.textAlign = 'center';
        errorMsg.style.padding = '10px';
        
        // 只添加一次错误提示
        if (!parent.querySelector('.img-error-msg')) {
          errorMsg.className = 'img-error-msg';
          parent.appendChild(errorMsg);
        }
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString();
    }
  }
};
</script>

<style scoped>
.detection-history {
  padding: 20px;
  margin-top: 20px;
}

.history-title {
  text-align: center;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: rgba(0, 0, 0, 0.4);
  border-radius: 8px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-item label {
  font-weight: 500;
  color: white;
  font-size: 14px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* 增强输入框对比度 */
.filter-item select,
.filter-item input[type="date"] {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  background-color: rgba(0, 0, 0, 0.3);
  color: white;
  min-width: 150px;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
}

/* 为下拉框添加箭头图标 */
.filter-item select {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='white' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14L2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 12px;
  padding-right: 30px;
}

/* 输入框焦点状态 */
.filter-item select:focus,
.filter-item input[type="date"]:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.3);
  background-color: rgba(0, 0, 0, 0.5);
}

/* 确保日期输入框中的文字可见 */
.filter-item input[type="date"]::-webkit-calendar-picker-indicator {
  filter: invert(1);
  opacity: 0.7;
}

/* 按钮样式增强 */
.filters .btn {
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  align-self: flex-end;
  margin-top: 20px;
  height: 36px;
}

.filters .btn:hover {
  background-color: #40a9ff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.dev-tools {
  margin-left: auto;
  padding: 5px 10px;
  background-color: #e8f4fc;
  border-radius: 4px;
  border: 1px dashed #007bff;
}

.mock-data-toggle {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9em;
  color: #007bff;
  cursor: pointer;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.history-item {
  border: 1px solid #ddd;
  border-radius: 5px;
  overflow: hidden;
}

.history-item-header {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #f9f9f9;
  border-bottom: 1px solid #ddd;
}

.history-content {
  display: flex;
  padding: 15px;
}

.history-image {
  flex: 1;
  margin-right: 15px;
  position: relative;
}

.history-image img {
  max-width: 100%;
  border-radius: 3px;
  min-height: 150px; /* 设置最小高度 */
}

.image-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 3px;
}

.detection-details {
  flex: 1;
}

.detection-list {
  margin-top: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.detection-item {
  padding: 8px;
  margin-bottom: 5px;
  background-color: #f5f5f5;
  border-radius: 3px;
}

.detection-class {
  font-weight: bold;
}

.detection-confidence {
  font-size: 0.9em;
  color: #666;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.loading, .error, .empty-history {
  text-align: center;
  padding: 20px;
}

.error {
  color: #f56c6c;
}
</style>
