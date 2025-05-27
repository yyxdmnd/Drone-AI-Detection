// 任务API处理函数
const API_URL = '/api/tasks/';

// 获取任务列表
async function fetchTasks() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`API响应错误: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('获取任务列表失败:', error);
        displayError('获取任务列表失败，请稍后再试。');
        return null;
    }
}

// 创建新任务
async function createTask(taskData) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData)
        });
        
        if (!response.ok) {
            throw new Error(`API响应错误: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('创建任务失败:', error);
        displayError('创建任务失败，请稍后再试。');
        return null;
    }
}

// 更新任务
async function updateTask(taskId, taskData) {
    try {
        const response = await fetch(`${API_URL}${taskId}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData)
        });
        
        if (!response.ok) {
            throw new Error(`API响应错误: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('更新任务失败:', error);
        displayError('更新任务失败，请稍后再试。');
        return null;
    }
}

// 删除任务
async function deleteTask(taskId) {
    try {
        const response = await fetch(`${API_URL}${taskId}/`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`API响应错误: ${response.status}`);
        }
        
        return true;
    } catch (error) {
        console.error('删除任务失败:', error);
        displayError('删除任务失败，请稍后再试。');
        return false;
    }
}

// 显示错误信息
function displayError(message) {
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
        
        // 5秒后自动隐藏错误信息
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 5000);
    } else {
        alert(message);
    }
} 