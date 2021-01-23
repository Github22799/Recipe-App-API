from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from core.models import User
from rest_framework.exceptions import ValidationError


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


class UserTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']
        user = authenticate(
            request=self.context['request'],
            username=email,
            password=password
        )

        if not user:
            msg = 'Provided credentials are wrong.'
            raise ValidationError(msg, code='Authentication')

        attrs['user'] = user
        return attrs
