from django.db import models
import os

def detection_upload_path(instance, filename):
    """定义上传文件的保存路径"""
    return os.path.join('detection_uploads', filename)

class DetectionImage(models.Model):
    """存储检测图像的模型"""
    image = models.ImageField(upload_to=detection_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    result_image = models.ImageField(upload_to='detection_results', null=True, blank=True)
    
    def __str__(self):
        return f"Detection {self.id} - {self.uploaded_at}"

class DetectionVideo(models.Model):
    """存储检测视频的模型"""
    video = models.FileField(upload_to=detection_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    result_video = models.FileField(upload_to='detection_results', null=True, blank=True)
    
    def __str__(self):
        return f"Video Detection {self.id} - {self.uploaded_at}"

class DetectionResult(models.Model):
    """存储检测结果的详细信息"""
    detection_image = models.ForeignKey(DetectionImage, on_delete=models.CASCADE, related_name='detection_results')
    class_name = models.CharField(max_length=100)  # 检测类别名称
    confidence = models.FloatField()  # 置信度
    x1 = models.FloatField()  # 边界框坐标
    y1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.class_name} ({self.confidence:.2f}) - {self.detection_image.id}"
    
    class Meta:
        ordering = ['-created_at']
