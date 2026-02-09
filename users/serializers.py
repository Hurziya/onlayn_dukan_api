from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Paydalanıwshılardı dizimnen ótkeriw hám profil maǵlıwmatların basqarıw ushın serializer.
    Paroldı qáwipsiz (xesh) túrde saqlawdı hám role maydanın qorǵawdı támiyinleydi.
    """
    class Meta:
        model = User
       
        fields = ['id', 'phone_number', 'email', 'password', 'first_name', 'last_name', 'address', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'read_only': True}
        }
 
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)