import os
from pathlib import Path
import torch
import numpy as np
from ultralytics import YOLO
from django.conf import settings
import base64
import cv2
import logging
import traceback

logger = logging.getLogger(__name__)

class YOLODetectionService:
    def __init__(self):
        # 模型文件路径
        model_path = os.path.join(settings.BASE_DIR, 'detection', 'ml_models', 'detect.pt')
        self.model = YOLO(model_path)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"YOLOv8 模型已加载，使用设备: {self.device}")

    def predict_image(self, image_path):
        """处理单张图片的检测"""
        try:
            # 运行推理
            results = self.model(image_path)
            
            # 处理结果
            result = results[0]
            output_image = result.plot()
            
            # 将检测结果转为JSON格式
            detection_results = []
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                
                detection_results.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': confidence,
                    'class_id': class_id,
                    'class_name': class_name
                })
            
            # 将结果图像编码为base64
            _, buffer = cv2.imencode('.jpg', output_image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                'status': 'success',
                'detections': detection_results,
                'image_base64': image_base64
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def predict_video(self, video_path, output_path=None):
        """处理视频的检测"""
        try:
            if output_path is None:
                # 生成输出视频路径
                filename = Path(video_path).stem
                output_path = os.path.join(settings.MEDIA_ROOT, f"{filename}_detected.mp4")
            
            # 运行视频推理
            results = self.model(video_path, save=True, project=os.path.dirname(output_path), name=os.path.basename(output_path).split('.')[0])
            
            # 视频结果统计
            detections_count = 0
            for r in results:
                detections_count += len(r.boxes)
            
            return {
                'status': 'success',
                'output_path': output_path,
                'detections_count': detections_count
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

# 创建单例服务实例
detection_service = YOLODetectionService()
