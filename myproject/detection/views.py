from django.shortcuts import render
import os
import tempfile
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .services import detection_service
from .models import DetectionImage, DetectionVideo, DetectionResult
from django.conf import settings
import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import DetectionImageSerializer, DetectionResultSerializer

# Create your views here.

class ImageDetectionView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        """处理图片上传和检测"""
        try:
            if 'image' not in request.FILES:
                return Response({'error': '没有上传图片'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 保存上传的图片
            image_obj = DetectionImage(image=request.FILES['image'])
            image_obj.save()
            
            # 获取图片路径
            image_path = os.path.join(settings.MEDIA_ROOT, image_obj.image.name)
            
            # 执行检测
            result = detection_service.predict_image(image_path)
            
            if result['status'] == 'success':
                # 存储检测结果到数据库
                
                # 保存结果图像
                result_image_name = f"result_{uuid.uuid4().hex}.jpg"
                image_obj.result_image.save(result_image_name, ContentFile(base64.b64decode(result['image_base64'])), save=True)
                
                # 存储每个检测结果
                for detection in result['detections']:
                    DetectionResult.objects.create(
                        detection_image=image_obj,
                        class_name=detection['class_name'],
                        confidence=detection['confidence'],
                        x1=detection['bbox'][0],
                        y1=detection['bbox'][1],
                        x2=detection['bbox'][2],
                        y2=detection['bbox'][3]
                    )
                
                # 将结果返回给前端
                return Response({
                    'message': '检测成功',
                    'image_id': image_obj.id,
                    'image_url': image_obj.image.url,
                    'result_image_url': image_obj.result_image.url,
                    'detections': result['detections']
                })
            else:
                return Response({
                    'error': result.get('message', '检测过程中发生错误')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VideoDetectionView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        """处理视频上传和检测"""
        if 'video' not in request.FILES:
            return Response({'error': '没有上传视频'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存上传的视频
        video_obj = DetectionVideo(video=request.FILES['video'])
        video_obj.save()
        
        # 获取视频路径
        video_path = os.path.join(settings.MEDIA_ROOT, video_obj.video.name)
        
        # 生成输出路径
        output_filename = f"result_{os.path.basename(video_path)}"
        output_path = os.path.join(settings.MEDIA_ROOT, 'detection_results', output_filename)
        
        # 执行检测
        result = detection_service.predict_video(video_path, output_path)
        
        if result['status'] == 'success':
            # 更新模型的结果视频字段
            video_obj.result_video = os.path.join('detection_results', output_filename)
            video_obj.save()
            
            # 将结果返回给前端
            return Response({
                'message': '视频检测成功',
                'video_id': video_obj.id,
                'video_url': video_obj.video.url,
                'result_video_url': video_obj.result_video.url,
                'detections_count': result['detections_count']
            })
        else:
            return Response({
                'error': result['message']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DetectionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """查看历史检测结果的视图集"""
    queryset = DetectionImage.objects.filter(result_image__isnull=False).order_by('-uploaded_at')
    serializer_class = DetectionImageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['detection_results__class_name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 使用 prefetch_related 优化查询性能
        queryset = queryset.prefetch_related('detection_results')
        
        # 根据检测类别过滤
        class_name = self.request.query_params.get('class_name', None)
        if class_name:
            queryset = queryset.filter(detection_results__class_name=class_name).distinct()
        
        # 根据日期范围过滤
        start_date = self.request.query_params.get('start_date', None)
        if start_date:
            queryset = queryset.filter(uploaded_at__gte=start_date)
            
        end_date = self.request.query_params.get('end_date', None)
        if end_date:
            queryset = queryset.filter(uploaded_at__lte=end_date)
            
        return queryset

# 添加新的视图类处理无人机数据
class DroneImageDetectionView(APIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        """处理无人机发送的实时图像流"""
        try:
            # 接收base64编码的图像
            if 'image_base64' in request.data:
                image_data = request.data['image_base64']
                
                # 去除base64前缀
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                
                # 解码base64
                image_bytes = base64.b64decode(image_data)
                
                # 创建临时文件保存图像
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_file.write(image_bytes)
                    image_path = temp_file.name
                
                # 创建DetectionImage记录
                image_obj = DetectionImage()
                image_obj.image.save(f"drone_image_{uuid.uuid4().hex}.jpg", 
                                     ContentFile(image_bytes), save=True)
                
                # 执行检测
                result = detection_service.predict_image(image_path)
                
                # 清理临时文件
                os.unlink(image_path)
                
                if result['status'] == 'success':
                    # 保存结果图像
                    result_image_name = f"result_{uuid.uuid4().hex}.jpg"
                    image_obj.result_image.save(
                        result_image_name, 
                        ContentFile(base64.b64decode(result['image_base64'])), 
                        save=True
                    )
                    
                    # 存储每个检测结果
                    for detection in result['detections']:
                        DetectionResult.objects.create(
                            detection_image=image_obj,
                            class_name=detection['class_name'],
                            confidence=detection['confidence'],
                            x1=detection['bbox'][0],
                            y1=detection['bbox'][1],
                            x2=detection['bbox'][2],
                            y2=detection['bbox'][3]
                        )
                    
                    # 检查是否发现污水
                    polluted_detections = [
                        det for det in result['detections'] 
                        if det['class_name'].lower() == 'polluted' and det['confidence'] > 0.5
                    ]
                    
                    # 将结果返回给无人机客户端
                    return Response({
                        'message': '检测成功',
                        'image_id': image_obj.id,
                        'image_url': image_obj.image.url,
                        'result_image_url': image_obj.result_image.url,
                        'detections': result['detections'],
                        'pollution_detected': len(polluted_detections) > 0,
                        'location_data': request.data.get('location', {})
                    })
                else:
                    return Response({
                        'error': result.get('message', '检测过程中发生错误')
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            else:
                return Response({
                    'error': '缺少图像数据'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
