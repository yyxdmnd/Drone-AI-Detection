from rest_framework import serializers
from .models import Task

# Create your tests here.

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
