from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken

class UserViewSet(viewsets.ModelViewSet):
    """
    Paydalanıwshılardı basqarıw ushın ViewSet.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        # Eger soraw jiberiwshi dizimnen ótpegen bolsa (create waqtında)
        if self.request.user.is_anonymous:
            return User.objects.none()
        # Admin barlıǵın kóredi, ápiwayı paydalanıwshı tek ózin
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get','patch'], url_path='me')
    def manage_profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        # PATCH (jańalaw)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token kiritilmegen"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist() 
            return Response({"message": "Siz sistemadan tabıslı shıqtıńız"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Token nadurıs yamasa aldın biykar etilgen"}, status=status.HTTP_400_BAD_REQUEST)