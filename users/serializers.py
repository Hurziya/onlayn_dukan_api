from rest_framework import serializers
from .models import User
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
User = get_user_model()



class UserSerializer(serializers.ModelSerializer):
    """
    Paydalanıwshılardı dizimnen ótkeriw hám profil maǵlıwmatların basqarıw ushın serializer.
    """

    class Meta:
        model = User
       
        fields = ['id', 'phone_number', 'telegram_id', 'password', 'first_name', 'last_name', 'address', 'role']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
            'role': {'read_only': True}
        }
 
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UserRegisterSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        
        fields = ('phone_number', 'first_name', 'last_name', 'email', 'password', 'password_confirm', 'address')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Paróller bir-birine sáykes kelmedi."})
        return attrs

    def create(self, validated_data):
        
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(**validated_data)
        return user