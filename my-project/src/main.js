import { createApp } from 'vue'
import App from './App.vue'
import './assets/style/variables.css'
import './assets/style/global.css'
import router from './router'

const app = createApp(App)
app.use(router)

// 添加控制台调试功能
window._vueApp = app;
window._vueRouter = router;
window.goToDetection = function() {
  router.push('/detection');
  console.log('已通过控制台函数跳转到检测页面');
}

app.mount('#app')

// 输出详细的路由配置，便于调试
console.log('Vue 应用已初始化');
console.log('路由配置:', router.getRoutes().map(route => ({
  path: route.path,
  name: route.name,
  component: route.components?.default?.name || '动态导入'
})));
