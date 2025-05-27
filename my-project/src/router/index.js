import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

// 定义更多路由，使用动态导入以提高性能
const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/detection',
    name: 'detection',
    // 动态导入方式加载组件
    component: () => import('../views/DetectionView.vue')
  },
  {
    path: '/tasks',
    name: 'tasks',
    // 方案1：直接使用已经存在的组件
    component: () => import('../components/TaskList.vue')
    
    // 方案2（如果创建了TasksView组件）:
    // component: () => import('../views/TasksView.vue')
  },
  {
    path: '/detection/history',
    name: 'detection-history',
    component: () => import('@/views/DetectionHistoryView.vue')
  },
  // 添加通配符路由，处理未匹配的路径
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 添加导航守卫，帮助调试
router.beforeEach((to, from, next) => {
  console.log(`路由导航: 从 ${from.path} 到 ${to.path}`);
  next();
});

export default router
