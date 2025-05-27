<template>
  <div class="detection-history-view">
    <h2 class="page-title">污水检测历史记录</h2>
    <DetectionHistory />
  </div>
</template>

<script>
import DetectionHistory from '@/components/DetectionHistory.vue';

export default {
  name: 'DetectionHistoryView',
  components: {
    DetectionHistory
  }
};
</script>

<style scoped>
.detection-history-view {
  padding: 20px;
}

.page-title {
  text-align: center;
  margin-bottom: 30px;
  color: var(--text-primary);
}
</style>
