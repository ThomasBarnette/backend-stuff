from rest_framework import serializers
from .models import Class, User

class ClassSerializer(serializers.ModelSerializer):
    # users = UserSerializer(many=True, read_only=True)  # Nested user data (optional)
    class Meta:
        model = Class
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    classes = ClassSerializer(many=True, read_only=True)  # Nested class data (optional)
    class Meta:
        model = User
        fields = '__all__'