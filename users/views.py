from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, LogoutSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    manage_profile=extend_schema(tags=['Profile']),
    logout=extend_schema(tags=['Auth']),
)
class UserViewSet(viewsets.ModelViewSet):
    """Paydalanıwshılar menedjmenti hám profil basqarıw ushın viewset"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return User.objects.none()
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @extend_schema(
        methods=['GET'],
        responses={200: UserSerializer},
        description="Login bolǵan paydalanıwshınıń óz profilin kóriwi"
    )
    @extend_schema(
        methods=['PATCH'],
        request=UserSerializer,
        responses={200: UserSerializer},
        description="Profil maǵlıwmatların jańalaw (tek kerekli maydanlardı jiberseńiz jetkilikli)"
    )
    @action(detail=False, methods=['get', 'patch'], url_path='me')
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
    
    @extend_schema(
        request=LogoutSerializer,
        responses={200: dict},
        description="Sistemadan shıǵıw (Refresh tokendi biykar etiw)"
    )
    @action(detail=False, methods=['post'])
    def logout(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist() 
            return Response({"message": "Siz sistemadan tabıslı shıqtıńız"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Token nadurıs yamasa aldın biykar etilgen"}, status=status.HTTP_400_BAD_REQUEST)