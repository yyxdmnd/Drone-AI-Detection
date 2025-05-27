from django.db import models
from django.contrib.auth.models import User

class DroneModel(models.Model):
    """无人机型号信息"""
    name = models.CharField(max_length=100)  # 如 'Mavic 3 Pro'
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class FlightMission(models.Model):
    """飞行任务模型"""
    MISSION_STATUS = (
        ('pending', '待执行'),
        ('in_progress', '执行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    )
    
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='missions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=MISSION_STATUS, default='pending')
    
    # 任务描述
    description = models.TextField(blank=True, null=True)
    
    # 地理边界（存储为GeoJSON）
    area_geojson = models.TextField(blank=True, null=True)
    
    # 飞行高度（米）
    altitude = models.FloatField(default=50.0)
    
    # 飞行速度（米/秒）
    speed = models.FloatField(default=5.0)
    
    # 航点间距（米）
    waypoint_distance = models.FloatField(default=20.0)
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

class Waypoint(models.Model):
    """航点模型"""
    mission = models.ForeignKey(FlightMission, on_delete=models.CASCADE, related_name='waypoints')
    order = models.IntegerField()  # 航点顺序
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()  # 高度（米）
    
    # 可选：在该点悬停时间（秒）
    hover_time = models.FloatField(default=0)
    
    # 可选：在该点执行特定动作（如拍照）
    take_photo = models.BooleanField(default=True)
    record_video = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"航点 {self.order} - 任务: {self.mission.name}"

class DronePhoto(models.Model):
    """无人机拍摄的照片"""
    mission = models.ForeignKey(FlightMission, on_delete=models.CASCADE, related_name='photos')
    waypoint = models.ForeignKey(Waypoint, on_delete=models.SET_NULL, null=True, related_name='photos')
    image = models.ImageField(upload_to='drone_photos/%Y/%m/%d/')
    
    # 地理位置
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    altitude = models.FloatField(null=True, blank=True)
    
    # 拍摄时间
    taken_at = models.DateTimeField(auto_now_add=True)
    
    # 可选：无人机朝向
    heading = models.FloatField(null=True, blank=True)
    
    # 关联到检测结果
    detection_result = models.ForeignKey('detection.DetectionImage', on_delete=models.SET_NULL, null=True, blank=True, related_name='drone_photos')
    
    def __str__(self):
        return f"照片 - 任务: {self.mission.name}, 时间: {self.taken_at}"
