import axios from 'axios';
import config from '@/config';

// 添加详细的日志信息
console.log('API 配置信息:', {
  baseURL: config.apiBaseUrl,
  environment: process.env.NODE_ENV
});

// 创建axios实例
const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 添加请求拦截器
apiClient.interceptors.request.use(config => {
  console.log('发送请求:', {
    url: config.url,
    method: config.method,
    headers: config.headers,
    data: config.data
  });
  return config;
});

// 添加响应拦截器
apiClient.interceptors.response.use(
  response => {
    console.log('收到响应:', {
      status: response.status,
      headers: response.headers,
      data: response.data
    });
    return response;
  },
  error => {
    console.error('请求错误:', {
      message: error.message,
      response: error.response,
      config: error.config
    });
    return Promise.reject(error);
  }
);

// 从本地存储获取任务
const getLocalTasks = () => {
  try {
    const tasksJSON = localStorage.getItem('tasks');
    if (!tasksJSON) return [];
    
    const parsed = JSON.parse(tasksJSON);
    // 确保返回的是数组
    if (!Array.isArray(parsed)) {
      console.error('本地存储的tasks不是数组:', parsed);
      return [];
    }
    return parsed;
  } catch (error) {
    console.error('读取本地任务失败:', error);
    return [];
  }
};

// 保存任务到本地存储
const saveLocalTasks = (tasks) => {
  try {
    // 确保tasks是数组
    if (!Array.isArray(tasks)) {
      console.error('尝试保存非数组tasks:', tasks);
      tasks = [];
    }
    localStorage.setItem('tasks', JSON.stringify(tasks));
  } catch (error) {
    console.error('保存本地任务失败:', error);
  }
};

// 创建模拟响应
const createMockResponse = (data, status = 200) => {
  return {
    data,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    headers: {},
    config: {}
  };
};

// eslint-disable-next-line no-unused-vars
const generateId = () => {
  return Math.random().toString(36).substr(2, 9);
};

// 双向同步本地数据和服务器数据
const syncWithServer = async () => {
  try {
    // 获取服务器数据
    const response = await apiClient.get('/tasks/');
    let serverTasks = [];
    
    // 处理可能的响应格式
    if (Array.isArray(response.data)) {
      serverTasks = response.data;
    } else if (response.data && Array.isArray(response.data.results)) {
      serverTasks = response.data.results;
    } else {
      console.error('服务器响应格式不符合预期:', response.data);
      return getLocalTasks(); // 返回本地数据
    }
    
    // 将服务器数据保存到本地
    saveLocalTasks(serverTasks);
    
    console.log('同步完成: 已从服务器获取', serverTasks.length, '个任务');
    return serverTasks;
  } catch (error) {
    console.error('与服务器同步失败:', error);
    return getLocalTasks(); // 失败时返回本地数据
  }
};

// 自动同步
const autoSync = () => {
  const syncInterval = 60000; // 1分钟同步一次
  console.log(`启动自动同步，间隔: ${syncInterval/1000}秒`);
  
  return setInterval(async () => {
    try {
      await syncWithServer();
      console.log('自动同步完成');
    } catch (error) {
      console.error('自动同步失败:', error);
    }
  }, syncInterval);
};

// API方法集
export default {
  // 获取任务列表
  async getTasks() {
    try {
      // 尝试从服务器获取数据
      const response = await apiClient.get('/tasks/');
      console.log('获取任务成功:', response);
      return response;
    } catch (error) {
      console.log('获取任务失败，使用本地数据:', error);
      // 如果服务器请求失败，使用本地存储的数据
      const localTasks = getLocalTasks();
      return createMockResponse(localTasks);
    }
  },

  // 创建任务
  async createTask(task) {
    try {
      // 打印请求数据，便于调试
      console.log('发送创建任务请求，数据:', task);
      
      // 格式化日期确保使用ISO格式
      const formattedTask = {
        ...task,
        created_at: new Date().toISOString()
      };
      
      // 发送请求到服务器
      const response = await apiClient.post('/tasks/', formattedTask);
      console.log('创建任务成功:', response);
      
      // 同时保存到本地
      const tasks = getLocalTasks();
      // 确保response.data包含有效数据
      if (!response.data) {
        console.error('创建任务响应中没有data字段:', response);
        throw new Error('服务器响应格式错误');
      }

      const newTask = { ...response.data, id: response.data.id || generateId() };
      saveLocalTasks([newTask, ...tasks]);
      
      return response;
    } catch (error) {
      // 更详细的错误日志
      console.error('创建任务失败:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        requestData: task
      });
      
      if (error.response && error.response.data) {
        // 如果服务器返回了详细错误信息，则抛出包含这些信息的错误
        throw new Error(`创建任务失败: ${JSON.stringify(error.response.data)}`);
      }
      
      // 如果服务器请求失败，仍然创建本地任务
      const tasks = getLocalTasks();
      const newTask = { ...task, id: generateId(), created_at: new Date().toISOString() };
      saveLocalTasks([newTask, ...tasks]);
      
      // 返回模拟响应
      return createMockResponse(newTask);
    }
  },

  // 更新任务
  async updateTask(id, task) {
    console.log('调用 updateTask 方法:', { id, task });
    
    if (!id) {
      console.error('无效的任务ID');
      return Promise.reject(new Error('无效的任务ID'));
    }
    
    try {
      const response = await apiClient.put(`/tasks/${id}/`, task);
      
      // 更新本地存储
      const localTasks = getLocalTasks();
      const index = localTasks.findIndex(t => t.id === id);
      if (index !== -1) {
        localTasks[index] = response.data;
        saveLocalTasks(localTasks);
      }
      
      return response;
    } catch (error) {
      console.error('更新任务失败:', error);
      throw error;
    }
  },

  // 删除任务
  async deleteTask(id) {
    console.log('调用 deleteTask 方法:', id);
    
    if (id === undefined || id === null) {
      console.error('无效的任务ID:', id);
      return Promise.reject(new Error('无效的任务ID'));
    }
    
    try {
      const response = await apiClient.delete(`/tasks/${id}/`);
      
      // 更新本地存储
      const localTasks = getLocalTasks();
      const updatedTasks = localTasks.filter(task => task.id !== id);
      saveLocalTasks(updatedTasks);
      
      return response;
    } catch (error) {
      // 特殊处理404错误 - 如果任务已经不存在，仍然从本地删除
      if (error.response && error.response.status === 404) {
        console.warn(`任务(ID:${id})不存在，已从本地存储删除`);
        const localTasks = getLocalTasks();
        const updatedTasks = localTasks.filter(task => task.id !== id);
        saveLocalTasks(updatedTasks);
        return createMockResponse({}, 204);
      }
      
      console.error('删除任务失败:', error);
      throw error;
    }
  },

  // 初始化API服务
  initialize() {
    console.log('API服务初始化');
    
    // 初始同步
    syncWithServer()
      .then(tasks => console.log('初始同步完成，共', tasks.length, '个任务'))
      .catch(error => console.error('初始同步失败:', error));
    
    // 启动自动同步
    const intervalId = autoSync();
    
    // 返回停止函数
    return () => {
      clearInterval(intervalId);
      console.log('API自动同步已停止');
    };
  },

  // 在api对象中添加
  setTasks(component, tasks) {
    // 确保任务数据的响应式更新
    if (component && Array.isArray(tasks)) {
      // 使用Vue.set或直接赋值以保持响应式
      component.tasks = [...tasks];
    }
  }
};

// 导出 apiClient 以便直接使用
export { apiClient };
