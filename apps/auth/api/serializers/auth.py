from rest_framework import serializers
from apps.auth.models import User
        
        
class UserRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField()
    phone_number = serializers.CharField()

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "first_name",
            "last_name",
            "middle_name",
            "phone_number",
        ]

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        first_name = attrs.get("first_name")
        last_name = attrs.get("last_name")
        middle_name = attrs.get("middle_name")
        phone_number = attrs.get("phone_number")

        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"username": "Bu username oldin ishlatilgan"}
            )

        if not first_name:
            raise serializers.ValidationError({"first_name": "Ismni kiritish shart"})

        if not last_name:
            raise serializers.ValidationError({"last_name": "Familyani kiritish shart"})

        if not middle_name:
            raise serializers.ValidationError(
                {"middle_name": "Sharif kiritilishi shart"}
            )

        if not password:
            raise serializers.ValidationError({"password": "Parolni kiritish shart"})

        if not phone_number:
            raise serializers.ValidationError({"phone_number": "Telefon raqam kiritish shart"})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user
