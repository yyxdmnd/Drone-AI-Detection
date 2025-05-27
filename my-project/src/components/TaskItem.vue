<template>
  <div class="task-item" :class="[statusClass, {'expanded': expanded}]">
    <div class="task-header" @click="toggleExpand">
      <div class="task-status-indicator" :class="statusClass"></div>
      
      <div class="task-main">
        <h3 class="task-title">{{ task.title }}</h3>
        <div class="task-meta">
          <span class="task-date">{{ formattedDate }}</span>
          <span class="task-divider">•</span>
          <span class="task-status-text">{{ statusText }}</span>
        </div>
      </div>
      
      <div class="task-priority" :class="priorityClass">
        {{ priorityText }}
      </div>
      
      <div class="task-expand-icon">
        {{ expanded ? '▼' : '▶' }}
      </div>
    </div>
    
    <div class="task-details" v-if="expanded">
      <p class="task-description" v-if="task.description">{{ task.description }}</p>
      <p class="task-empty-description" v-else>暂无任务描述</p>
      
      <div class="task-extra-info">
        <div class="task-info-item">
          <span class="info-label">创建时间:</span>
          <span class="info-value">{{ fullDateTime }}</span>
        </div>
        <div class="task-info-item" v-if="task.assigned_to">
          <span class="info-label">指派给:</span>
          <span class="info-value">{{ task.assigned_to }}</span>
        </div>
        <div class="task-info-item" v-if="task.location">
          <span class="info-label">位置:</span>
          <span class="info-value">{{ task.location }}</span>
        </div>
      </div>
      
      <div class="task-actions">
        <button @click.stop="$emit('edit', task)" class="task-action-btn edit-btn">
          <span class="action-icon">✏️</span>
          <span class="action-text">编辑</span>
        </button>
        <button @click.stop="confirmDelete" class="task-action-btn delete-btn">
          <span class="action-icon">🗑️</span>
          <span class="action-text">删除</span>
        </button>
        <button @click.stop="startTask" class="task-action-btn start-btn" v-if="task.status === 'pending'">
          <span class="action-icon">▶️</span>
          <span class="action-text">开始</span>
        </button>
        <button @click.stop="completeTask" class="task-action-btn complete-btn" v-if="task.status === 'in_progress'">
          <span class="action-icon">✓</span>
          <span class="action-text">完成</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TaskItem',
  props: {
    task: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      expanded: false
    };
  },
  computed: {
    statusClass() {
      return `status-${this.task.status}`;
    },
    statusText() {
      const statusMap = {
        'pending': '待处理',
        'in_progress': '进行中',
        'completed': '已完成'
      };
      return statusMap[this.task.status] || this.task.status;
    },
    priorityClass() {
      const priorityMap = {
        1: 'priority-highest',
        2: 'priority-high',
        3: 'priority-medium',
        4: 'priority-low',
        5: 'priority-lowest'
      };
      return priorityMap[this.task.priority] || 'priority-medium';
    },
    priorityText() {
      const priorityMap = {
        1: '最高',
        2: '高',
        3: '中',
        4: '低',
        5: '最低'
      };
      return priorityMap[this.task.priority] || '中';
    },
    formattedDate() {
      if (!this.task.created_at) return '';
      
      try {
        const date = new Date(this.task.created_at);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        // 今天创建的显示时间
        if (diffDays === 0) {
          return `今天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
        }
        
        // 昨天创建的显示"昨天"
        if (diffDays === 1) {
          return '昨天';
        }
        
        // 一周内创建的显示星期几
        if (diffDays < 7) {
          const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
          return days[date.getDay()];
        }
        
        // 其他显示具体日期
        return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
      } catch (e) {
        return this.task.created_at;
      }
    },
    fullDateTime() {
      if (!this.task.created_at) return '';
      
      try {
        const date = new Date(this.task.created_at);
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        });
      } catch (e) {
        return this.task.created_at;
      }
    }
  },
  methods: {
    toggleExpand() {
      this.expanded = !this.expanded;
    },
    confirmDelete() {
      if (confirm(`确定要删除任务 "${this.task.title}" 吗？`)) {
        this.$emit('delete', this.task);
      }
    },
    startTask() {
      const updatedTask = { ...this.task, status: 'in_progress' };
      this.$emit('edit', updatedTask);
    },
    completeTask() {
      const updatedTask = { ...this.task, status: 'completed' };
      this.$emit('edit', updatedTask);
    }
  }
};
</script>

<style scoped>
.task-item {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: var(--border-radius-base);
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: var(--shadow-base);
}

.task-item:hover {
  box-shadow: var(--shadow-large);
}

.task-item.expanded {
  background-color: rgba(255, 255, 255, 0.08);
}

.task-header {
  display: flex;
  align-items: center;
  padding: var(--spacing-md);
  cursor: pointer;
}

.task-status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: var(--spacing-md);
}

.task-main {
  flex: 1;
}

.task-title {
  margin: 0 0 10px 0;
  font-size: 1.2rem;
  word-break: break-word;
}

.task-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #999;
}

.task-date {
  margin-right: var(--spacing-md);
}

.task-divider {
  margin: 0 var(--spacing-md);
}

.task-status-text {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.task-priority {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
}

.priority-highest {
  background-color: #cf1322;
  color: white;
}

.priority-high {
  background-color: #ff4d4f;
  color: white;
}

.priority-medium {
  background-color: #faad14;
  color: #000;
}

.priority-low {
  background-color: #52c41a;
  color: white;
}

.priority-lowest {
  background-color: #13c2c2;
  color: white;
}

.task-details {
  padding: var(--spacing-md);
}

.task-description {
  margin: 0 0 10px 0;
  color: #bbb;
  line-height: 1.5;
  word-break: break-word;
}

.task-empty-description {
  margin: 0 0 10px 0;
  color: #999;
  text-align: center;
}

.task-extra-info {
  margin-bottom: var(--spacing-md);
}

.task-info-item {
  margin-bottom: var(--spacing-xs);
}

.info-label {
  font-weight: 500;
}

.info-value {
  margin-left: var(--spacing-xs);
}

.task-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

.task-action-btn {
  background: transparent;
  border: none;
  color: #bbb;
  font-size: 1.2rem;
  cursor: pointer;
  margin-bottom: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;
}

.task-action-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.edit-btn:hover {
  color: var(--primary-color);
}

.delete-btn:hover {
  color: var(--danger-color);
}

.task-expand-icon {
  margin-left: var(--spacing-md);
}
</style> 