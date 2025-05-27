<template>
  <div class="drone-mission-view">
    <h2 class="page-title">无人机污水监测任务</h2>
    
    <!-- 任务列表 -->
    <div class="mission-list-container">
      <h3 class="section-title">飞行任务列表</h3>
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <span>加载中...</span>
      </div>
      <div v-else-if="missions.length === 0" class="empty-state">
        <p>暂无飞行任务</p>
        <button @click="showMissionForm = true" class="btn btn-primary">
          创建新任务
        </button>
      </div>
      <div v-else class="mission-list">
        <div v-for="mission in missions" :key="mission.id" class="mission-card">
          <div class="mission-header">
            <h4>{{ mission.name }}</h4>
            <span :class="['status-badge', 'status-' + mission.status]">
              {{ getMissionStatusText(mission.status) }}
            </span>
          </div>
          <div class="mission-info">
            <p>{{ mission.description }}</p>
            <div class="mission-details">
              <span>航点数量: {{ mission.waypoints.length }}</span>
              <span>照片数量: {{ mission.photos_count }}</span>
              <span>飞行高度: {{ mission.altitude }}米</span>
            </div>
          </div>
          <div class="mission-actions">
            <button 
              v-if="mission.status === 'pending'" 
              @click="startMission(mission.id)" 
              class="btn btn-success"
            >
              开始任务
            </button>
            <button 
              v-if="mission.status === 'in_progress'" 
              @click="completeMission(mission.id)" 
              class="btn btn-info"
            >
              完成任务
            </button>
            <button 
              v-if="['pending', 'in_progress'].includes(mission.status)" 
              @click="cancelMission(mission.id)" 
              class="btn btn-danger"
            >
              取消任务
            </button>
            <button @click="viewMissionDetails(mission.id)" class="btn btn-secondary">
              查看详情
            </button>
          </div>
        </div>
      </div>
      <div class="add-mission-btn">
        <button @click="showMissionForm = true" class="btn btn-primary">
          创建新任务
        </button>
      </div>
    </div>
    
    <!-- 任务创建表单 -->
    <div v-if="showMissionForm" class="mission-form-modal">
      <div class="mission-form-container">
        <h3>创建新的飞行任务</h3>
        <form @submit.prevent="createMission">
          <div class="form-group">
            <label for="name">任务名称</label>
            <input 
              type="text" 
              id="name" 
              v-model="newMission.name" 
              class="input" 
              required
            >
          </div>
          <div class="form-group">
            <label for="description">任务描述</label>
            <textarea 
              id="description" 
              v-model="newMission.description" 
              class="input"
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="altitude">飞行高度(米)</label>
            <input 
              type="number" 
              id="altitude" 
              v-model.number="newMission.altitude" 
              class="input" 
              min="10" 
              max="500"
            >
          </div>
          <div class="form-group">
            <label for="speed">飞行速度(米/秒)</label>
            <input 
              type="number" 
              id="speed" 
              v-model.number="newMission.speed" 
              class="input" 
              min="1" 
              max="15"
            >
          </div>
          <div class="form-actions">
            <button type="button" @click="showMissionForm = false" class="btn btn-secondary">
              取消
            </button>
            <button type="submit" class="btn btn-primary">
              保存任务
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 任务详情 -->
    <div v-if="selectedMission" class="mission-details-modal">
      <div class="mission-details-container">
        <h3>任务详情: {{ selectedMission.name }}</h3>
        <div class="mission-detail-content">
          <div class="mission-info-panel">
            <h4>基本信息</h4>
            <div class="detail-row">
              <span class="detail-label">状态:</span>
              <span :class="['status-badge', 'status-' + selectedMission.status]">
                {{ getMissionStatusText(selectedMission.status) }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">描述:</span>
              <span>{{ selectedMission.description }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">创建时间:</span>
              <span>{{ formatDateTime(selectedMission.created_at) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">飞行高度:</span>
              <span>{{ selectedMission.altitude }}米</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">飞行速度:</span>
              <span>{{ selectedMission.speed }}米/秒</span>
            </div>
          </div>
          
          <div class="waypoints-panel">
            <h4>航点信息</h4>
            <div v-if="selectedMission.waypoints.length === 0" class="empty-state">
              <p>暂无航点数据</p>
            </div>
            <div v-else class="waypoints-list">
              <div v-for="waypoint in selectedMission.waypoints" :key="waypoint.id" class="waypoint-item">
                <div class="waypoint-header">
                  <span>航点 #{{ waypoint.order }}</span>
                </div>
                <div class="waypoint-details">
                  <div class="waypoint-location">
                    <div>纬度: {{ waypoint.latitude }}</div>
                    <div>经度: {{ waypoint.longitude }}</div>
                    <div>高度: {{ waypoint.altitude }}米</div>
                  </div>
                  <div class="waypoint-actions">
                    <div>悬停: {{ waypoint.hover_time }}秒</div>
                    <div>拍照: {{ waypoint.take_photo ? '是' : '否' }}</div>
                    <div>录像: {{ waypoint.record_video ? '是' : '否' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="photos-panel">
            <h4>任务照片</h4>
            <div v-if="isLoadingPhotos" class="loading-state">
              <div class="spinner"></div>
              <span>加载照片...</span>
            </div>
            <div v-else-if="missionPhotos.length === 0" class="empty-state">
              <p>暂无照片数据</p>
            </div>
            <div v-else class="photos-grid">
              <div v-for="photo in missionPhotos" :key="photo.id" class="photo-item">
                <div class="photo-thumbnail">
                  <img :src="photo.image" alt="任务照片">
                </div>
                <div class="photo-info">
                  <div>时间: {{ formatDateTime(photo.taken_at) }}</div>
                  <div v-if="photo.detection_result">
                    <span :class="{ 'pollution-detected': hasWastewater(photo) }">
                      {{ hasWastewater(photo) ? '发现污水' : '未发现污水' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="detail-actions">
          <button @click="selectedMission = null" class="btn btn-secondary">
            关闭
          </button>
          <button v-if="selectedMission.status === 'pending'" @click="showWaypointEditor = true" class="btn btn-primary">
            编辑航点
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import config from '@/config';

export default {
  name: 'DroneMissionView',
  data() {
    return {
      missions: [],
      isLoading: true,
      showMissionForm: false,
      selectedMission: null,
      missionPhotos: [],
      isLoadingPhotos: false,
      showWaypointEditor: false,
      newMission: {
        name: '',
        description: '',
        altitude: 50,
        speed: 5,
        waypoint_distance: 20
      }
    };
  },
  mounted() {
    this.fetchMissions();
  },
  methods: {
    async fetchMissions() {
      this.isLoading = true;
      try {
        const response = await axios.get(`${config.apiBaseUrl}/drone/missions/`);
        this.missions = response.data;
      } catch (error) {
        console.error('获取任务列表失败:', error);
      } finally {
        this.isLoading = false;
      }
    },
    async createMission() {
      try {
        await axios.post(`${config.apiBaseUrl}/drone/missions/`, this.newMission);
        this.showMissionForm = false;
        this.fetchMissions();
        this.newMission = {
          name: '',
          description: '',
          altitude: 50,
          speed: 5,
          waypoint_distance: 20
        };
      } catch (error) {
        console.error('创建任务失败:', error);
      }
    },
    async viewMissionDetails(missionId) {
      try {
        const response = await axios.get(`${config.apiBaseUrl}/drone/missions/${missionId}/`);
        this.selectedMission = response.data;
        this.fetchMissionPhotos(missionId);
      } catch (error) {
        console.error('获取任务详情失败:', error);
      }
    },
    async fetchMissionPhotos(missionId) {
      this.isLoadingPhotos = true;
      try {
        const response = await axios.get(`${config.apiBaseUrl}/drone/photos/`, {
          params: { mission_id: missionId }
        });
        this.missionPhotos = response.data;
      } catch (error) {
        console.error('获取任务照片失败:', error);
      } finally {
        this.isLoadingPhotos = false;
      }
    },
    getMissionStatusText(status) {
      const statusMap = {
        'pending': '待执行',
        'in_progress': '执行中',
        'completed': '已完成',
        'failed': '失败',
        'cancelled': '已取消'
      };
      return statusMap[status] || status;
    },
    formatDateTime(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    hasWastewater(photo) {
      if (!photo.detection_result || !photo.detection_result.detection_results) {
        return false;
      }
      
      return photo.detection_result.detection_results.some(
        det => det.class_name.toLowerCase() === 'polluted' && det.confidence > 0.5
      );
    },
    async startMission(missionId) {
      try {
        await axios.post(`${config.apiBaseUrl}/drone/mission/${missionId}/control/`, {
          action: 'start'
        });
        this.fetchMissions();
        if (this.selectedMission && this.selectedMission.id === missionId) {
          this.viewMissionDetails(missionId);
        }
      } catch (error) {
        console.error('开始任务失败:', error);
      }
    },
    async completeMission(missionId) {
      try {
        await axios.post(`${config.apiBaseUrl}/drone/mission/${missionId}/control/`, {
          action: 'complete'
        });
        this.fetchMissions();
        if (this.selectedMission && this.selectedMission.id === missionId) {
          this.viewMissionDetails(missionId);
        }
      } catch (error) {
        console.error('完成任务失败:', error);
      }
    },
    async cancelMission(missionId) {
      if (!confirm('确定要取消此任务吗？')) {
        return;
      }
      
      try {
        await axios.post(`${config.apiBaseUrl}/drone/mission/${missionId}/control/`, {
          action: 'cancel'
        });
        this.fetchMissions();
        if (this.selectedMission && this.selectedMission.id === missionId) {
          this.viewMissionDetails(missionId);
        }
      } catch (error) {
        console.error('取消任务失败:', error);
      }
    }
  }
};
</script>

<style scoped>
/* 样式省略，可根据您的应用风格定制 */
</style>
