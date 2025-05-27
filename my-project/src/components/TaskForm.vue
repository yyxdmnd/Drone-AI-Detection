<template>
  <div class="task-form">
    <h3>{{ isEditing ? '编辑任务' : '添加新任务' }}</h3>
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="task-title">任务标题: <span class="required">*</span></label>
        <input 
          id="task-title" 
          v-model="taskData.title" 
          placeholder="请输入任务标题" 
          required
        >
      </div>
      
      <div class="form-group">
        <label for="task-description">任务描述:</label>
        <textarea 
          id="task-description" 
          v-model="taskData.description" 
          placeholder="请输入任务描述"
          rows="3"
        ></textarea>
      </div>
      
      <div class="form-row">
        <div class="form-group half">
          <label for="task-status">任务状态: <span class="required">*</span></label>
          <select id="task-status" v-model="taskData.status" required>
            <option value="待处理">待处理</option>
            <option value="进行中">进行中</option>
            <option value="已完成">已完成</option>
          </select>
        </div>
        
        <div class="form-group half">
          <label for="task-priority">优先级:</label>
          <select id="task-priority" v-model="taskData.priority">
            <option value="低">低</option>
            <option value="中">中</option>
            <option value="高">高</option>
          </select>
        </div>
      </div>
      
      <div class="form-group">
        <label for="task-due-date">截止日期:</label>
        <input 
          id="task-due-date" 
          type="date" 
          v-model="taskData.due_date"
        >
      </div>
      
      <div class="form-actions">
        <button type="submit" class="submit-btn">
          {{ isEditing ? '更新任务' : '添加任务' }}
        </button>
        <button type="button" @click="resetForm" class="reset-btn">重置</button>
      </div>
    </form>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'TaskForm',
  props: {
    task: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      taskData: {
        title: '',
        description: '',
        status: '待处理',
        priority: '中',
        due_date: null
      }
    };
  },
  computed: {
    isEditing() {
      return this.task !== null;
    }
  },
  created() {
    if (this.isEditing) {
      this.taskData = { ...this.task };
    }
  },
  methods: {
    async submitForm() {
      try {
        let response;
        
        if (this.isEditing) {
          response = await api.updateTask(this.task.id, this.taskData);
          this.$emit('task-updated', response.data);
        } else {
          response = await api.createTask(this.taskData);
          this.$emit('task-created', response.data);
        }
        
        this.resetForm();
      } catch (error) {
        console.error('提交任务失败:', error);
      }
    },
    resetForm() {
      if (!this.isEditing) {
        this.taskData = {
          title: '',
          description: '',
          status: '待处理',
          priority: '中',
          due_date: null
        };
      } else {
        this.$emit('cancel-edit');
      }
    }
  }
};
</script>

<style scoped>
.task-form {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid #eee;
}

.form-group {
  margin-bottom: 15px;
}

.form-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.half {
  flex: 1;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.required {
  color: red;
}

input, select, textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

textarea {
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.submit-btn {
  background-color: #1890ff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

.reset-btn {
  background-color: #f5f5f5;
  border: 1px solid #d9d9d9;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 15px;
  }
}
</style>
