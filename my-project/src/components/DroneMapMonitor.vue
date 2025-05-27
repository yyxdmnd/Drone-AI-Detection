<template>
  <div class="map-container">
    <div class="map-header">
      <div class="map-title">
        <i class="map-icon">📍</i>
        <span>无人机定位监控</span>
      </div>
      <div class="view-controls">
        <button @click="changeMapType('satellite')" :class="{ active: mapType === 'satellite' }">卫星图</button>
        <button @click="changeMapType('terrain')" :class="{ active: mapType === 'terrain' }">地形图</button>
        <button @click="changeMapType('road')" :class="{ active: mapType === 'road' }">路线图</button>
      </div>
    </div>
    
    <div class="map-content">
      <div id="echarts-map" ref="echartsMap"></div>
      
      <div class="map-controls">
        <button @click="zoomIn" class="map-control-btn">+</button>
        <button @click="zoomOut" class="map-control-btn">-</button>
        <button @click="followDrone" class="map-control-btn" :class="{ active: isFollowing }">
          <span class="follow-icon">⟲</span>
        </button>
      </div>
      
      <div class="drone-info">
        <div class="info-item">
          <span class="info-label">当前坐标:</span>
          <span class="info-value">{{ currentPosition[0].toFixed(6) }}, {{ currentPosition[1].toFixed(6) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">飞行高度:</span>
          <span class="info-value">{{ altitude }}米</span>
        </div>
        <div class="info-item">
          <span class="info-label">飞行速度:</span>
          <span class="info-value">{{ speed }}米/秒</span>
        </div>
        <div class="info-item">
          <span class="info-label">电量:</span>
          <span class="info-value">
            <div class="battery-indicator">
              <div class="battery-level" :style="{ width: `${batteryLevel}%`, backgroundColor: batteryColor }"></div>
            </div>
            {{ batteryLevel }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  name: 'DroneMapMonitor',
  props: {
    initialPosition: {
      type: Array,
      default: () => [30.542, 114.298] // 武汉市坐标
    }
  },
  data() {
    return {
      mapChart: null,
      mapType: 'satellite',
      isFollowing: true,
      currentPosition: [30.542, 114.298],
      routePoints: [],
      altitude: 120,
      speed: 8.5,
      batteryLevel: 78,
      zoomLevel: 12
    };
  },
  computed: {
    batteryColor() {
      if (this.batteryLevel > 50) return '#52c41a';
      if (this.batteryLevel > 20) return '#faad14';
      return '#f5222d';
    }
  },
  mounted() {
    this.initMap();
    window.addEventListener('resize', this.resizeMap);
    
    // 模拟无人机移动
    this.simulateDroneMovement();
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.resizeMap);
    if (this.moveTimer) {
      clearInterval(this.moveTimer);
    }
  },
  methods: {
    initMap() {
      const mapElement = this.$refs.echartsMap;
      if (!mapElement) {
        console.error('Map element not found');
        return;
      }
      
      this.mapChart = echarts.init(mapElement);
      this.updateMap();
    },
    
    updateMap() {
      // 准备地图数据
      this.routePoints.push([...this.currentPosition]);
      if (this.routePoints.length > 100) {
        // 限制路径点数量，防止性能问题
        this.routePoints.shift();
      }
      
      // 创建地图配置
      const option = {
        backgroundColor: this.getMapBackground(),
        title: {
          text: '无人机飞行轨迹',
          left: 'center',
          textStyle: {
            color: '#eee'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: params => {
            if (params.seriesType === 'scatter') {
              return `当前位置<br/>经度: ${params.value[0].toFixed(6)}<br/>纬度: ${params.value[1].toFixed(6)}`;
            }
            return '';
          }
        },
        legend: {
          data: ['历史轨迹', '当前位置'],
          textStyle: {
            color: '#eee'
          },
          right: 10,
          top: 10
        },
        geo: {
          map: 'china',
          roam: true,
          zoom: this.zoomLevel,
          center: this.isFollowing ? this.currentPosition : undefined,
          itemStyle: {
            areaColor: this.getAreaColor(),
            borderColor: '#111'
          },
          emphasis: {
            itemStyle: {
              areaColor: '#2a333d'
            },
            label: {
              show: false
            }
          }
        },
        series: [
          {
            name: '历史轨迹',
            type: 'lines',
            coordinateSystem: 'geo',
            data: [{
              coords: this.routePoints
            }],
            lineStyle: {
              color: '#1890ff',
              width: 2,
              opacity: 0.8,
              curveness: 0.1
            },
            effect: {
              show: true,
              period: 6,
              trailLength: 0.5,
              color: '#fff',
              symbolSize: 3
            }
          },
          {
            name: '当前位置',
            type: 'effectScatter',
            coordinateSystem: 'geo',
            data: [this.currentPosition],
            symbolSize: 15,
            itemStyle: {
              color: '#f5222d'
            },
            rippleEffect: {
              scale: 5,
              brushType: 'stroke'
            },
            hoverAnimation: true,
            zlevel: 1
          }
        ]
      };
      
      this.mapChart.setOption(option);
    },
    
    simulateDroneMovement() {
      const generateRandomOffset = () => (Math.random() - 0.5) * 0.002;
      
      this.moveTimer = setInterval(() => {
        // 更新位置，模拟无人机移动
        this.currentPosition = [
          this.currentPosition[0] + generateRandomOffset(),
          this.currentPosition[1] + generateRandomOffset()
        ];
        
        // 随机更新其他数据
        this.altitude = Math.max(80, Math.min(150, this.altitude + (Math.random() - 0.5) * 5));
        this.speed = Math.max(5, Math.min(12, this.speed + (Math.random() - 0.5) * 1));
        this.batteryLevel = Math.max(1, Math.min(100, this.batteryLevel - 0.1));
        
        // 更新地图
        this.updateMap();
      }, 2000);
    },
    
    resizeMap() {
      if (this.mapChart) {
        this.mapChart.resize();
      }
    },
    
    changeMapType(type) {
      this.mapType = type;
      this.updateMap();
    },
    
    getMapBackground() {
      switch (this.mapType) {
        case 'satellite': return '#061e30';
        case 'terrain': return '#2E4053';
        case 'road': return '#121212';
        default: return '#061e30';
      }
    },
    
    getAreaColor() {
      switch (this.mapType) {
        case 'satellite': return '#0d2e4a';
        case 'terrain': return '#3d5466';
        case 'road': return '#2a2a2a';
        default: return '#0d2e4a';
      }
    },
    
    zoomIn() {
      this.zoomLevel = Math.min(20, this.zoomLevel + 1);
      this.updateMap();
    },
    
    zoomOut() {
      this.zoomLevel = Math.max(1, this.zoomLevel - 1);
      this.updateMap();
    },
    
    followDrone() {
      this.isFollowing = !this.isFollowing;
      this.updateMap();
    }
  }
};
</script>

<style scoped>
.map-container {
  background-color: #222;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #333;
  color: white;
}

.map-title {
  display: flex;
  align-items: center;
  font-weight: bold;
}

.map-icon {
  margin-right: 8px;
}

.view-controls {
  display: flex;
}

.view-controls button {
  background: transparent;
  border: 1px solid #555;
  color: #bbb;
  padding: 4px 10px;
  margin-left: 5px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.view-controls button.active {
  background-color: #1890ff;
  border-color: #1890ff;
  color: white;
}

.map-content {
  position: relative;
  height: 400px;
}

#echarts-map {
  width: 100%;
  height: 100%;
}

.map-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  flex-direction: column;
}

.map-control-btn {
  width: 36px;
  height: 36px;
  margin-bottom: 8px;
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid #555;
  color: white;
  font-size: 18px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.map-control-btn.active {
  background-color: #1890ff;
  border-color: #1890ff;
}

.follow-icon {
  font-size: 16px;
}

.drone-info {
  position: absolute;
  left: 10px;
  bottom: 10px;
  background: rgba(0, 0, 0, 0.7);
  padding: 12px;
  border-radius: 4px;
  color: white;
  font-size: 0.9rem;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  align-items: center;
}

.info-label {
  width: 80px;
  color: #bbb;
}

.battery-indicator {
  width: 60px;
  height: 10px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 5px;
  margin-right: 8px;
  overflow: hidden;
  display: inline-block;
}

.battery-level {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s, background-color 0.5s;
}
</style>
