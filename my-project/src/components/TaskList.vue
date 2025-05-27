<template>
  <div class="task-list-container card">
    <div class="task-list-header">
      <h2>任务管理中心</h2>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showCreateForm = true">
          <span class="icon">➕</span>新建任务
        </button>
        <button v-if="isDevelopment" 
                @click="debugCreateTask" 
                class="btn" 
                style="background-color: #722ed1;">
          测试API
        </button>
      </div>
    </div>
    
    <!-- 任务筛选 -->
    <div class="task-filters">
      <div class="search-box">
        <input 
          type="text" 
          v-model="filters.searchQuery" 
          placeholder="搜索任务..." 
          class="input search-input"
          @input="handleFilterChange"
          @keydown.enter="applySearch"
        />
        <button class="search-button" @click="applySearch">
          <span class="search-icon">🔍</span>
        </button>
      </div>
      
      <div class="filter-controls">
        <select v-model="filters.statusFilter" @change="handleFilterChange" class="input select-input">
          <option value="all">所有状态</option>
          <option value="pending">待处理</option>
          <option value="in_progress">进行中</option>
          <option value="completed">已完成</option>
        </select>
        
        <select v-model="filters.sortOption" @change="handleFilterChange" class="input select-input">
          <option value="newest">最新创建</option>
          <option value="oldest">最早创建</option>
          <option value="priority">优先级</option>
          <option value="name-asc">名称 A-Z</option>
          <option value="name-desc">名称 Z-A</option>
        </select>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="spinner-large"></div>
      <p>加载任务中...</p>
    </div>
    
    <!-- 错误信息 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      <span>{{ error }}</span>
      <button class="error-close" @click="error = null">×</button>
    </div>
    
    <!-- 任务列表 -->
    <transition-group name="list" tag="div" class="task-items">
      <div v-if="!loading && filteredTasks.length === 0" class="empty-list" key="empty">
        <div class="empty-icon">📋</div>
        <p>{{ tasks.length === 0 ? '暂无任务，请添加新任务。' : '没有符合筛选条件的任务。' }}</p>
        <button v-if="tasks.length === 0" class="btn btn-primary" @click="showCreateForm = true">创建第一个任务</button>
      </div>
      
      <TaskItem 
        v-for="task in paginatedTasks" 
        :key="task.id" 
        :task="task"
        @edit="handleEdit"
        @delete="handleDelete"
        class="task-item"
      />
    </transition-group>
    
    <!-- 分页组件 -->
    <TaskPagination 
      v-if="filteredTasks.length > 0"
      :current-page="pagination.currentPage"
      :total-pages="totalPages"
      :page-size="pagination.pageSize"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    />
    
    <!-- 创建任务对话框 -->
    <div v-if="showCreateForm" class="dialog-overlay">
      <div class="dialog-content">
        <div class="dialog-header">
          <h3>创建新任务</h3>
          <button class="dialog-close" @click="showCreateForm = false">×</button>
        </div>
        <form @submit.prevent="handleCreateTask" class="task-form">
          <div class="form-group">
            <label for="task-title">任务标题 <span class="required">*</span></label>
            <input 
              id="task-title" 
              v-model="newTask.title" 
              type="text" 
              class="input"
              required
              placeholder="输入任务标题"
            >
          </div>
          
          <div class="form-group">
            <label for="task-description">任务描述</label>
            <textarea 
              id="task-description" 
              v-model="newTask.description"
              class="input textarea"
              rows="3"
              placeholder="输入任务详细描述"
            ></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group half">
              <label for="task-status">任务状态</label>
              <select id="task-status" v-model="newTask.status" class="input">
                <option value="pending">待处理</option>
                <option value="in_progress">进行中</option>
                <option value="completed">已完成</option>
              </select>
            </div>
            
            <div class="form-group half">
              <label for="task-priority">优先级</label>
              <select id="task-priority" v-model="newTask.priority" class="input">
                <option value="高">最高</option>
                <option value="高">高</option>
                <option value="中">中</option>
                <option value="低">低</option>
                <option value="低">最低</option>
              </select>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="showCreateForm = false" class="btn btn-cancel">取消</button>
            <button type="submit" class="btn btn-primary">创建任务</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 编辑任务对话框 -->
    <div v-if="showEditForm" class="dialog-overlay">
      <div class="dialog-content">
        <div class="dialog-header">
          <h3>编辑任务</h3>
          <button class="dialog-close" @click="closeEditForm">×</button>
        </div>
        <form @submit.prevent="submitEditForm" class="task-form">
          <div class="form-group">
            <label for="edit-title">任务标题 <span class="required">*</span></label>
            <input 
              id="edit-title" 
              v-model="currentEditingTask.title" 
              type="text"
              class="input" 
              required
            >
          </div>
          
          <div class="form-group">
            <label for="edit-description">任务描述</label>
            <textarea 
              id="edit-description" 
              v-model="currentEditingTask.description"
              class="input textarea"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group half">
              <label for="edit-status">任务状态</label>
              <select id="edit-status" v-model="currentEditingTask.status" class="input">
                <option value="pending">待处理</option>
                <option value="in_progress">进行中</option>
                <option value="completed">已完成</option>
              </select>
            </div>
            
            <div class="form-group half">
              <label for="edit-priority">优先级</label>
              <select id="edit-priority" v-model="currentEditingTask.priority" class="input">
                <option value="高">最高</option>
                <option value="高">高</option>
                <option value="中">中</option>
                <option value="低">低</option>
                <option value="低">最低</option>
              </select>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeEditForm" class="btn btn-cancel">取消</button>
            <button type="submit" class="btn btn-primary">保存修改</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import TaskItem from './TaskItem.vue';
import TaskPagination from './TaskPagination.vue';
import axios from 'axios';
import config from '@/config';

export default {
  name: 'TaskList',
  components: {
    TaskItem,
    TaskPagination
  },
  data() {
    return {
      tasks: [],
      loading: true,
      error: null,
      filters: {
        searchQuery: '',
        statusFilter: 'all',
        sortOption: 'newest'
      },
      pagination: {
        currentPage: 1,
        pageSize: 5 // 改为5条/页
      },
      showEditForm: false,
      currentEditingTask: null,
      showCreateForm: false,
      newTask: {
        title: '',
        description: '',
        status: 'pending',
        priority: '中'
      },
      isDevelopment: process.env.NODE_ENV === 'development',
      requestCount: 0,  // 添加请求计数器
      searchDebounce: null
    };
  },
  computed: {
    filteredTasks() {
      // 防御性检查 this.tasks 是否为数组
      if (!Array.isArray(this.tasks)) {
        console.error('tasks 不是数组:', this.tasks);
        return [];
      }
      
      let result = [...this.tasks];
      
      // 应用搜索筛选
      if (this.filters.searchQuery) {
        const query = this.filters.searchQuery.toLowerCase();
        result = result.filter(task => 
          task.title.toLowerCase().includes(query) || 
          (task.description && task.description.toLowerCase().includes(query))
        );
      }
      
      // 应用状态筛选
      if (this.filters.statusFilter !== 'all') {
        result = result.filter(task => task.status === this.filters.statusFilter);
      }
      
      // 应用排序
      // 首先过滤掉无效项
      result = result.filter(item => item !== null && item !== undefined);
      
      switch(this.filters.sortOption) {
        case 'newest':
          result.sort((a, b) => {
            if (!a || !a.created_at) return 1;
            if (!b || !b.created_at) return -1;
            return new Date(b.created_at) - new Date(a.created_at);
          });
          break;
        case 'oldest':
          result.sort((a, b) => {
            if (!a || !a.created_at) return 1;
            if (!b || !b.created_at) return -1;
            return new Date(a.created_at) - new Date(b.created_at);
          });
          break;
        case 'name-asc':
          result.sort((a, b) => {
            if (!a || !a.title) return 1;
            if (!b || !b.title) return -1;
            return a.title.localeCompare(b.title);
          });
          break;
        case 'name-desc':
          result.sort((a, b) => {
            if (!a || !a.title) return 1;
            if (!b || !b.title) return -1;
            return b.title.localeCompare(a.title);
          });
          break;
        case 'priority': {
          const priorityOrder = { '高': 0, '中': 1, '低': 2 };
          result.sort((a, b) => {
            if (!a || !a.priority) return 1;
            if (!b || !b.priority) return -1;
            return priorityOrder[a.priority] - priorityOrder[b.priority];
          });
          break;
        }
        case 'due-date':
          result.sort((a, b) => {
            if (!a) return 1;
            if (!b) return -1;
            if (!a.due_date) return 1;
            if (!b.due_date) return -1;
            return new Date(a.due_date) - new Date(b.due_date);
          });
          break;
      }
      
      return result;
    },
    paginatedTasks() {
      const startIndex = (this.pagination.currentPage - 1) * this.pagination.pageSize;
      const endIndex = startIndex + this.pagination.pageSize;
      return this.filteredTasks.slice(startIndex, endIndex);
    },
    totalPages() {
      return Math.ceil(this.filteredTasks.length / this.pagination.pageSize);
    }
  },
  methods: {
    async fetchTasks() {
      this.loading = true;
      this.error = null;
      this.requestCount++;
      
      console.group(`任务列表请求 #${this.requestCount}`);
      console.time('请求耗时');
      
      try {
        console.log('开始请求任务列表...');
        const response = await api.getTasks();
        
        console.log('请求成功:', {
          status: response.status,
          statusText: response.statusText,
          data: response.data
        });

        if (Array.isArray(response.data)) {
          this.tasks = response.data;
        } else if (response.data && Array.isArray(response.data.results)) {
          this.tasks = response.data.results;
        } else {
          console.error('API响应格式不符合预期:', response.data);
          this.error = '数据格式错误，请联系管理员';
        }
        
        this.debugInfo = {
          requestInfo: {
            time: new Date().toISOString(),
            url: response.config.url,
            method: response.config.method
          },
          responseInfo: {
            status: response.status,
            statusText: response.statusText,
            dataLength: response.data.length
          },
          data: response.data
        };
      } catch (error) {
        console.error('请求失败:', error);
        this.error = `请求失败: ${error.message}`;
        this.debugInfo = {
          error: {
            message: error.message,
            response: error.response ? {
              status: error.response.status,
              data: error.response.data
            } : null
          }
        };
      } finally {
        this.loading = false;
        console.timeEnd('请求耗时');
        console.groupEnd();
      }
    },
    
    handleTaskCreated(newTask) {
      this.tasks.push(newTask);
    },
    
    handleTaskUpdated(updatedTask) {
      const index = this.tasks.findIndex(task => task.id === updatedTask.id);
      if (index !== -1) {
        this.tasks.splice(index, 1, updatedTask);
      }
    },
    
    handleTaskDeleted(taskId) {
      if (!taskId) {
        console.error('收到无效的任务ID进行删除操作');
        this.error = '删除任务失败:无效的任务ID';
        return;
      }
      
      console.log('成功删除任务，ID:', taskId);
      this.tasks = this.tasks.filter(task => task.id !== taskId);
      
      // 可选：显示成功消息
      setTimeout(() => {
        this.error = null;
      }, 2000);
    },
    
    handleTaskError(errorMessage) {
      this.error = errorMessage;
      
      // 刷新任务列表以确保数据同步
      this.fetchTasks();
    },
    
    handleFilterChange() {
      // 应用过滤条件时重置到第一页
      this.pagination.currentPage = 1;
      // 添加防抖，避免频繁触发查询
      if (this.searchDebounce) {
        clearTimeout(this.searchDebounce);
      }
      this.searchDebounce = setTimeout(() => {
        this.applySearch();
      }, 300);
    },
    
    applySearch() {
      console.log("应用搜索:", this.filters.searchQuery);
      // 清除任何现有的防抖
      if (this.searchDebounce) {
        clearTimeout(this.searchDebounce);
      }
      // 如果搜索条件变化较大，可以考虑重新从服务器获取数据
      // 但对于简单的客户端筛选，可以直接依赖 computed 属性
      
      // 可以在这里添加额外的搜索逻辑
    },
    
    handlePageChange(page) {
      this.pagination.currentPage = page;
    },
    
    handlePageSizeChange(pageSize) {
      this.pagination.pageSize = pageSize;
      this.pagination.currentPage = 1; // 重置到第一页
    },
    
    handleEdit(task) {
      this.currentEditingTask = JSON.parse(JSON.stringify(task)); // 创建深拷贝
      this.showEditForm = true;
    },
    
    handleDelete(task) {
      // 确认并删除任务
      console.log('删除任务:', task);
      if (confirm(`确定要删除任务"${task.title}"吗？`)) {
        this.handleTaskDeleted(task.id);
      }
    },
    
    closeEditForm() {
      this.showEditForm = false;
      this.currentEditingTask = null;
    },
    
    async submitEditForm() {
      if (!this.currentEditingTask) return;
      
      try {
        const updatedTask = await api.updateTask(
          this.currentEditingTask.id, 
          this.currentEditingTask
        );
        this.handleTaskUpdated(updatedTask);
        this.closeEditForm();
      } catch (error) {
        console.error('更新任务失败:', error);
        this.handleTaskError('更新任务失败: ' + error.message);
      }
    },
    
    handleCreateTask() {
      // 验证任务数据
      if (!this.newTask.title.trim()) {
        this.error = "任务标题不能为空";
        return;
      }
      
      const task = {
        title: this.newTask.title.trim(),
        description: this.newTask.description ? this.newTask.description.trim() : '',
        status: this.newTask.status || 'pending',
        priority: this.newTask.priority,
        created_at: new Date().toISOString()
      };
      
      this.loading = true;
      api.createTask(task)
        .then(response => {
          // 确保响应数据有效
          if (!response || !response.data) {
            throw new Error('服务器响应格式错误');
          }
          
          // 防御性检查，确保tasks是数组
          if (!Array.isArray(this.tasks)) {
            console.error('tasks不是数组，重置为空数组');
            this.tasks = [];
          }
          
          this.tasks.unshift(response.data);
          this.showCreateForm = false;
          this.resetNewTask();
          this.showToast('任务创建成功', 'success');
        })
        .catch(error => {
          console.error("创建任务失败", error);
          // 显示更友好的错误信息
          let errorMsg = '创建任务失败';
          
          if (error.response && error.response.data) {
            if (typeof error.response.data === 'string') {
              errorMsg += ': ' + error.response.data;
            } else if (typeof error.response.data === 'object') {
              // 格式化对象错误信息
              const errorDetails = Object.entries(error.response.data)
                .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
                .join('; ');
              
              errorMsg += ': ' + errorDetails;
            }
          } else {
            errorMsg += ': ' + error.message;
          }
          
          this.error = errorMsg;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    resetNewTask() {
      this.newTask = {
        title: '',
        description: '',
        status: 'pending',
        priority: '中'
      };
    },
    
    showToast(message, type) {
      this.$root.$emit('show-toast', message, type);
    },
    
    debugCreateTask() {
      // 准备基本的任务数据
      const testTask = {
        title: "测试任务",
        description: "这是一个用于测试API的任务",
        status: "pending",
        priority: "中",
        created_at: new Date().toISOString()
      };
      
      console.log('开始测试创建任务...');
      console.log('发送数据:', testTask);
      
      // 尝试发送请求
      axios.post(`${config.apiBaseUrl}/tasks/`, testTask)
        .then(response => {
          console.log('测试成功:', response.data);
          
          // 防御性检查，确保tasks是数组
          if (!Array.isArray(this.tasks)) {
            console.error('tasks不是数组，重置为空数组');
            this.tasks = [];
          }
          
          // 确保响应包含有效数据
          if (response.data) {
            // 添加到任务列表
            this.tasks.unshift(response.data);
          }
          
          this.showToast('测试创建成功', 'success');
        })
        .catch(error => {
          console.error('测试失败:', {
            message: error.message,
            status: error.response?.status,
            data: error.response?.data
          });
          this.error = `测试创建失败: ${error.response?.status} - ${JSON.stringify(error.response?.data || {})}`;
        });
    }
  },
  created() {
    console.log('TaskList 组件已创建');
  },
  mounted() {
    console.log('TaskList 组件已挂载');
    
    // 先获取任务列表
    this.fetchTasks();
    
    // 确保下拉框显示正确的初始值
    this.$nextTick(() => {
      // 选择所有下拉框并设置初始样式
      const selects = document.querySelectorAll('.select-input');
      selects.forEach(select => {
        // 在组件挂载完成后，强制触发一次change事件
        if (select.value) {
          select.classList.add('has-value');
          
          // 触发一个虚拟的change事件，确保v-model绑定的值正确反映
          const event = new Event('change', { bubbles: true });
          select.dispatchEvent(event);
        }
        
        // 监听变化
        select.addEventListener('change', function() {
          if (this.value) {
            this.classList.add('has-value');
          } else {
            this.classList.remove('has-value');
          }
        });
      });
    });
    
    // 初始化搜索框状态
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
      searchInput.addEventListener('focus', function() {
        this.closest('.search-box').classList.add('active');
      });
      
      searchInput.addEventListener('blur', function() {
        if (!this.value) {
          this.closest('.search-box').classList.remove('active');
        }
      });
    }
  }
};
</script>

<style scoped>
.task-list-container {
  max-width: 100%;
  width: 100%;
}

.task-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.task-filters {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-lg);
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 200px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  border-radius: var(--border-radius-base);
  overflow: hidden;
}

.search-input {
  padding-left: 36px;
  height: 40px;
  border-radius: var(--border-radius-base);
  border: 1px solid rgba(255, 255, 255, 0.2);
  background-color: rgba(0, 0, 0, 0.3);
  transition: all 0.3s;
  width: 100%;
  color: white;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
  background-color: rgba(0, 0, 0, 0.4);
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.7);
  z-index: 1;
}

.search-button {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all 0.3s;
}

.search-button:hover {
  color: var(--primary-color);
}

.search-button:focus {
  outline: none;
}

.search-box.active .search-icon,
.search-input:focus + .search-button {
  color: var(--primary-color);
}

.filter-controls {
  display: flex;
  gap: var(--spacing-md);
}

.select-input {
  min-width: 150px;
  height: 40px;
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--border-radius-base);
  background-color: rgba(0, 0, 0, 0.3);
  transition: all 0.3s;
  cursor: pointer;
  font-weight: 500;
  color: white !important;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='white' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14L2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 12px;
  padding-right: 2.5rem;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.select-input:hover {
  border-color: var(--primary-color);
  background-color: rgba(0, 0, 0, 0.4);
}

.select-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.4);
  outline: none;
  background-color: rgba(0, 0, 0, 0.5);
}

.select-input option {
  padding: 10px;
  background-color: #333;
  color: white;
  font-weight: normal;
}

@media (max-width: 768px) {
  .task-filters {
    flex-direction: column;
  }
  
  .filter-controls {
    width: 100%;
  }
  
  .select-input {
    width: 100%;
  }
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl) 0;
  color: var(--text-secondary);
}

.spinner-large {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
}

.error-message {
  display: flex;
  align-items: center;
  background-color: rgba(245, 34, 45, 0.1);
  border: 1px solid rgba(245, 34, 45, 0.2);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  color: var(--danger-color);
}

.error-icon {
  margin-right: var(--spacing-md);
}

.error-close {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--text-disabled);
  cursor: pointer;
  font-size: 18px;
}

.task-items {
  margin-bottom: var(--spacing-lg);
}

.empty-list {
  text-align: center;
  padding: var(--spacing-xl) 0;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--spacing-md);
  opacity: 0.5;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background-color: var(--card-bg);
  border-radius: var(--border-radius-large);
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-large);
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--divider-color);
}

.dialog-header h3 {
  margin: 0;
}

.dialog-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-disabled);
  cursor: pointer;
}

.task-form {
  padding: var(--spacing-md);
}

.form-group {
  margin-bottom: var(--spacing-md);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  color: var(--text-secondary);
}

.required {
  color: var(--danger-color);
}

.textarea {
  resize: vertical;
}

.form-row {
  display: flex;
  gap: var(--spacing-md);
}

.half {
  flex: 1;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

.btn-cancel {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

/* 添加动画效果 */
.list-enter-active, .list-leave-active {
  transition: all 0.3s;
}
.list-enter, .list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.task-item {
  margin-bottom: var(--spacing-md);
}

/* 应用于创建和编辑任务表单中的下拉菜单 */
.task-form .input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--divider-color);
  border-radius: var(--border-radius-base);
  transition: all 0.3s;
  background-color: white;
  color: var(--text-primary);
}

.task-form select.input {
  padding-right: 30px;
  cursor: pointer;
  font-weight: 500;
}

.task-form .input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
  outline: none;
}

/* 优先级选择框特殊样式 - 增强可见性 */
#task-priority, #edit-priority {
  font-weight: 500;
  color: #333;
}

#task-priority option[value="高"], #edit-priority option[value="高"] {
  color: var(--danger-color);
  font-weight: bold;
  background-color: rgba(245, 34, 45, 0.05);
}

#task-priority option[value="中"], #edit-priority option[value="中"] {
  color: var(--warning-color);
  font-weight: bold;
  background-color: rgba(250, 173, 20, 0.05);
}

#task-priority option[value="低"], #edit-priority option[value="低"] {
  color: var(--secondary-color);
  font-weight: bold;
  background-color: rgba(82, 196, 26, 0.05);
}

/* 任务状态选择框特殊样式 - 增强可见性 */
#task-status, #edit-status {
  color: #333;
}

#task-status option[value="pending"], #edit-status option[value="pending"] {
  color: var(--warning-color);
  background-color: rgba(250, 173, 20, 0.05);
}

#task-status option[value="in_progress"], #edit-status option[value="in_progress"] {
  color: var(--primary-color);
  background-color: rgba(24, 144, 255, 0.05);
}

#task-status option[value="completed"], #edit-status option[value="completed"] {
  color: var(--secondary-color);
  background-color: rgba(82, 196, 26, 0.05);
}

/* 确保下拉框选中值的样式 */
.select-input.has-value {
  font-weight: 600;
  color: var(--text-primary);
}

/* 修复Firefox和某些浏览器中下拉箭头不显示的问题 */
@-moz-document url-prefix() {
  .select-input {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%23333' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14L2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E") !important;
  }
}

/* 确保IE11下拉箭头正常显示 */
select::-ms-expand {
  display: none;
}

/* 增强下拉菜单在聚焦时的视觉效果 */
.select-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.15);
}

/* 增强下拉菜单初始状态 */
.filter-controls .select-input {
  position: relative;
  font-weight: 600;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
}

/* 添加背景渐变效果增强可见性 */
.filter-controls .select-input {
  background-image: 
    linear-gradient(to bottom, rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.3)),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='white' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14L2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* 修复Firefox特别是下拉菜单背景图的问题 */
@-moz-document url-prefix() {
  .filter-controls .select-input {
    background-image: 
      linear-gradient(to bottom, rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.3)),
      url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='white' viewBox='0 0 16 16'%3E%3Cpath d='M7.247 11.14L2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat;
    background-position: right 0.75rem center;
  }
}

/* 解决Safari和某些浏览器下拉菜单兼容性问题 */
@media screen and (-webkit-min-device-pixel-ratio: 0) {
  .select-input {
    background-color: rgba(0, 0, 0, 0.3) !important;
    color: white !important;
  }
}

/* 为红框里的下拉菜单添加显眼的边框 */
.task-filters .filter-controls .select-input {
  border: 1px solid rgba(255, 255, 255, 0.4);
}
</style>
