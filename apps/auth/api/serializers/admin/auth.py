from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

from apps.auth.models import User

class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        assert user
        if not user.is_active or not user.is_staff or not user.is_superuser:
            raise AuthenticationFailed(
                "Siz admin foydalanuvchi emassiz!", code="no_access"
            )
        return data

class AdminTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])
        
        user_id = refresh['user_id']
        user = User.objects.get(
            id=user_id
        )
        
        if not user.is_staff or not user.is_superuser:
            raise AuthenticationFailed("Kechirasiz lekin siz admin emassiz")
        
        data = {}
        data = {}
        data["access"] = str(refresh.access_token)
        
        return data

class UserAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "middle_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "password",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
