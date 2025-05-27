<template>
  <div class="tasks-view">
    <h2 class="page-title">任务管理</h2>
    <TaskList />
  </div>
</template>

<script>
import TaskList from '@/components/TaskList.vue'

export default {
  name: 'TasksView',
  components: {
    TaskList
  }
}
</script>

<style scoped>
.tasks-view {
  padding: 20px;
}

.page-title {
  text-align: center;
  margin-bottom: 30px;
  color: var(--text-primary);
}
</style>
