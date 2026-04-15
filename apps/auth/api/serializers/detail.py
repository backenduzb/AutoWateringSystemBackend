from apps.auth.models import User
from rest_framework import serializers



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "middle_name", "password"]
        read_only_fields = ["id", "username"]

    def validate(self, attrs):
        if "username" in attrs:
            username = attrs.get("username")
            if not username:
                raise serializers.ValidationError({"username": "Usernameni kiritish shart"})
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError(
                    {"username": "Bu username allaqachon ishlatilingan"}
                )
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None) 
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
    
        if password:  
            instance.set_password(password) 
    
        instance.save()
        return instance