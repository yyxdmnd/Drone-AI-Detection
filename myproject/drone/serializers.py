from rest_framework import serializers
from .models import DroneModel, FlightMission, Waypoint, DronePhoto
from detection.serializers import DetectionImageSerializer

class DroneModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneModel
        fields = '__all__'

class WaypointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waypoint
        fields = '__all__'

class DronePhotoSerializer(serializers.ModelSerializer):
    detection_result = DetectionImageSerializer(read_only=True)
    
    class Meta:
        model = DronePhoto
        fields = '__all__'
        read_only_fields = ('mission', 'waypoint', 'detection_result')

class FlightMissionCreateSerializer(serializers.ModelSerializer):
    waypoints = WaypointSerializer(many=True, required=False)
    
    class Meta:
        model = FlightMission
        fields = ('id', 'name', 'description', 'area_geojson', 'altitude', 
                  'speed', 'waypoint_distance', 'waypoints', 'status')
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        waypoints_data = validated_data.pop('waypoints', [])
        mission = FlightMission.objects.create(**validated_data)
        
        for i, waypoint_data in enumerate(waypoints_data):
            Waypoint.objects.create(mission=mission, order=i+1, **waypoint_data)
        
        return mission

class FlightMissionSerializer(serializers.ModelSerializer):
    waypoints = WaypointSerializer(many=True, read_only=True)
    photos_count = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = FlightMission
        fields = ('id', 'name', 'description', 'created_by', 'created_by_username',
                  'created_at', 'updated_at', 'status', 'area_geojson',
                  'altitude', 'speed', 'waypoint_distance', 'waypoints', 
                  'photos_count')
    
    def get_photos_count(self, obj):
        return obj.photos.count()
