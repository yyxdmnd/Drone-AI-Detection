from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from .models import DroneModel, FlightMission, Waypoint, DronePhoto
from .serializers import (
    DroneModelSerializer, FlightMissionSerializer, 
    WaypointSerializer, DronePhotoSerializer,
    FlightMissionCreateSerializer
)
from django.shortcuts import get_object_or_404
import json
import base64
import tempfile
from django.core.files.base import ContentFile
from detection.services import detection_service

# Create your views here.

# 无人机模型视图集
class DroneModelViewSet(viewsets.ModelViewSet):
    queryset = DroneModel.objects.all()
    serializer_class = DroneModelSerializer

# 飞行任务视图集
class FlightMissionViewSet(viewsets.ModelViewSet):
    queryset = FlightMission.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FlightMissionCreateSerializer
        return FlightMissionSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# 航点视图集
class WaypointViewSet(viewsets.ModelViewSet):
    queryset = Waypoint.objects.all()
    serializer_class = WaypointSerializer
    
    def get_queryset(self):
        mission_id = self.request.query_params.get('mission_id')
        if mission_id:
            return Waypoint.objects.filter(mission_id=mission_id).order_by('order')
        return Waypoint.objects.all()

# 无人机照片视图集
class DronePhotoViewSet(viewsets.ModelViewSet):
    queryset = DronePhoto.objects.all().order_by('-taken_at')
    serializer_class = DronePhotoSerializer
    
    def get_queryset(self):
        mission_id = self.request.query_params.get('mission_id')
        if mission_id:
            return DronePhoto.objects.filter(mission_id=mission_id)
        return DronePhoto.objects.all()

# 无人机实时数据接收API
class DroneDataReceiverView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # 解析请求数据
            data = request.data
            mission_id = data.get('mission_id')
            image_data = data.get('image_data')  # Base64编码的图像
            location_data = data.get('location', {})
            
            if not mission_id or not image_data:
                return Response({
                    'error': '缺少必要参数'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取飞行任务
            mission = get_object_or_404(FlightMission, id=mission_id)
            
            # 将Base64图像转换为文件
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_data = base64.b64decode(imgstr)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False) as temp_file:
                temp_file.write(image_data)
                temp_file_path = temp_file.name
            
            # 执行检测
            detection_result = detection_service.predict_image(temp_file_path)
            
            # 保存无人机照片
            drone_photo = DronePhoto(
                mission=mission,
                latitude=location_data.get('latitude'),
                longitude=location_data.get('longitude'),
                altitude=location_data.get('altitude'),
                heading=location_data.get('heading'),
            )
            
            # 保存原始图像
            drone_photo.image.save(
                f"drone_image_{mission_id}_{drone_photo.taken_at.strftime('%Y%m%d%H%M%S')}.{ext}", 
                ContentFile(image_data),
                save=False
            )
            
            # 如果有关联的航点信息
            waypoint_id = data.get('waypoint_id')
            if waypoint_id:
                waypoint = get_object_or_404(Waypoint, id=waypoint_id)
                drone_photo.waypoint = waypoint
            
            drone_photo.save()
            
            # 进行污水检测并关联结果
            if detection_result['status'] == 'success':
                from detection.models import DetectionImage, DetectionResult
                
                # 创建检测图像记录
                detection_img = DetectionImage(image=drone_photo.image)
                
                # 保存检测结果图像
                result_image_data = base64.b64decode(detection_result['image_base64'])
                detection_img.result_image.save(
                    f"result_{drone_photo.image.name.split('/')[-1]}", 
                    ContentFile(result_image_data),
                    save=True
                )
                
                # 保存各个检测结果
                for detection in detection_result['detections']:
                    DetectionResult.objects.create(
                        detection_image=detection_img,
                        class_name=detection['class_name'],
                        confidence=detection['confidence'],
                        x1=detection['bbox'][0],
                        y1=detection['bbox'][1],
                        x2=detection['bbox'][2],
                        y2=detection['bbox'][3]
                    )
                
                # 关联到无人机照片
                drone_photo.detection_result = detection_img
                drone_photo.save()
                
                # 检查是否有污水
                has_pollution = any(
                    det['class_name'].lower() == 'polluted' and det['confidence'] > 0.5 
                    for det in detection_result['detections']
                )
                
                return Response({
                    'message': '数据接收成功',
                    'drone_photo_id': drone_photo.id,
                    'detection_result_id': detection_img.id,
                    'detection_results': detection_result['detections'],
                    'pollution_detected': has_pollution
                })
            else:
                return Response({
                    'message': '数据接收成功，但检测失败',
                    'drone_photo_id': drone_photo.id,
                    'error': detection_result.get('message', '未知错误')
                })
                
        except Exception as e:
            return Response({
                'error': f'处理数据时出错: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 任务控制API
class MissionControlView(APIView):
    def post(self, request, mission_id, *args, **kwargs):
        """开始、暂停或取消任务"""
        action = request.data.get('action')
        mission = get_object_or_404(FlightMission, id=mission_id)
        
        if action == 'start':
            mission.status = 'in_progress'
            mission.save()
            return Response({'message': f'任务 {mission.name} 已开始'})
        
        elif action == 'pause':
            # 暂停任务逻辑
            return Response({'message': f'任务 {mission.name} 已暂停'})
            
        elif action == 'cancel':
            mission.status = 'cancelled'
            mission.save()
            return Response({'message': f'任务 {mission.name} 已取消'})
            
        elif action == 'complete':
            mission.status = 'completed'
            mission.save()
            return Response({'message': f'任务 {mission.name} 已完成'})
            
        return Response({
            'error': '无效的操作'
        }, status=status.HTTP_400_BAD_REQUEST)
