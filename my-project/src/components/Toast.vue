<template>
  <div class="toast-container" v-if="visible">
    <div class="toast" :class="type">
      {{ message }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppToast',
  data() {
    return {
      visible: false,
      message: '',
      type: 'info', // info, success, error, warning
      timeout: null
    };
  },
  methods: {
    show(message, type = 'info', duration = 3000) {
      this.message = message;
      this.type = type;
      this.visible = true;
      
      // 清除之前的定时器
      if (this.timeout) {
        clearTimeout(this.timeout);
      }
      
      // 设置自动隐藏
      this.timeout = setTimeout(() => {
        this.visible = false;
      }, duration);
    }
  }
};
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
}

.toast {
  padding: 12px 20px;
  border-radius: 4px;
  background-color: #f5f5f5;
  color: #333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  margin-bottom: 10px;
  min-width: 250px;
}

.toast.success {
  background-color: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}

.toast.error {
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
}

.toast.warning {
  background-color: #fffbe6;
  border: 1px solid #ffe58f;
  color: #faad14;
}

.toast.info {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
  color: #1890ff;
}
</style>
