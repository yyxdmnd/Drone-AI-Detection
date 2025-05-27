from rest_framework import serializers
from .models import DetectionImage, DetectionResult, DetectionVideo

class DetectionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionResult
        fields = ['id', 'class_name', 'confidence', 'x1', 'y1', 'x2', 'y2', 'created_at']

class DetectionImageSerializer(serializers.ModelSerializer):
    detection_results = DetectionResultSerializer(many=True, read_only=True)
    results_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DetectionImage
        fields = ['id', 'image', 'result_image', 'uploaded_at', 'detection_results', 'results_count']
    
    def get_results_count(self, obj):
        return obj.detection_results.count()
