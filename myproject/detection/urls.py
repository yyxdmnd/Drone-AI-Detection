from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ImageDetectionView, VideoDetectionView, 
    DetectionHistoryViewSet, DroneImageDetectionView
)

router = DefaultRouter()
router.register(r'history', DetectionHistoryViewSet)

urlpatterns = [
    path('image/', ImageDetectionView.as_view(), name='image_detection'),
    path('video/', VideoDetectionView.as_view(), name='video_detection'),
    path('drone/image/', DroneImageDetectionView.as_view(), name='drone_image_detection'),
    path('', include(router.urls)),  # 包含检测历史API
]
