<template>
  <div class="task-filter">
    <div class="search-box">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="搜索任务..." 
        @input="applyFilters"
      >
    </div>
    <div class="filter-options">
      <div class="status-filter">
        <span class="filter-label">状态筛选:</span>
        <select v-model="statusFilter" @change="applyFilters">
          <option value="all">全部</option>
          <option value="待处理">待处理</option>
          <option value="进行中">进行中</option>
          <option value="已完成">已完成</option>
        </select>
      </div>
      <div class="priority-filter">
        <span class="filter-label">优先级:</span>
        <select v-model="priorityFilter" @change="applyFilters">
          <option value="all">全部</option>
          <option value="低">低</option>
          <option value="中">中</option>
          <option value="高">高</option>
        </select>
      </div>
      <div class="sort-options">
        <span class="filter-label">排序方式:</span>
        <select v-model="sortOption" @change="applyFilters">
          <option value="newest">最新创建</option>
          <option value="oldest">最早创建</option>
          <option value="name-asc">名称 (A-Z)</option>
          <option value="name-desc">名称 (Z-A)</option>
          <option value="priority">优先级</option>
          <option value="due-date">到期日</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TaskFilter',
  data() {
    return {
      searchQuery: '',
      statusFilter: 'all',
      priorityFilter: 'all',
      sortOption: 'newest'
    };
  },
  methods: {
    applyFilters() {
      this.$emit('filter-changed', {
        searchQuery: this.searchQuery,
        statusFilter: this.statusFilter,
        priorityFilter: this.priorityFilter,
        sortOption: this.sortOption
      });
    }
  }
};
</script>

<style scoped>
.task-filter {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid #eee;
}

.search-box {
  margin-bottom: 15px;
}

.search-box input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.status-filter, .priority-filter, .sort-options {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 200px;
}

.filter-label {
  margin-right: 8px;
  font-weight: bold;
}

select {
  padding: 6px;
  border: 1px solid #ddd;
  border-radius: 4px;
  flex-grow: 1;
}

@media (max-width: 768px) {
  .filter-options {
    flex-direction: column;
    gap: 10px;
  }
  
  .status-filter, .priority-filter, .sort-options {
    width: 100%;
  }
}
</style>
