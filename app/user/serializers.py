from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': User.PASS_MIN_LENGTH
            }
        }

    def create(self, validated_fields):
        return get_user_model().objects.create_user(**validated_fields)