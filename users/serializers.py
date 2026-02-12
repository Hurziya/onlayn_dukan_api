from rest_framework import serializers
from .models import User


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