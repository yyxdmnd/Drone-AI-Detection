from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DroneModelViewSet, FlightMissionViewSet, WaypointViewSet, 
    DronePhotoViewSet, DroneDataReceiverView, MissionControlView
)

router = DefaultRouter()
router.register(r'drones', DroneModelViewSet)
router.register(r'missions', FlightMissionViewSet)
router.register(r'waypoints', WaypointViewSet)
router.register(r'photos', DronePhotoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('data/receive/', DroneDataReceiverView.as_view(), name='drone_data_receiver'),
    path('mission/<int:mission_id>/control/', MissionControlView.as_view(), name='mission_control'),
]
