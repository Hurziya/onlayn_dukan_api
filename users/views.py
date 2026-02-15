from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import User
from .serializers import UserRegisterSerializer, UserSerializer, LogoutSerializer

@extend_schema_view(
    manage_profile=extend_schema(tags=['Profile']),
    logout=extend_schema(tags=['Auth']),
    create=extend_schema(
        tags=['Auth'], 
        summary="Dizimnen ótiw (Registratsiya)",
        description="Jańa paydalanıwshı jaratıw. Tabıslı ótse, tokenlar qaytarıladı.",
        responses={201: UserSerializer}
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return User.objects.none()
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    # Registratsiya procesin customizatsiya qılamız
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Registratsiyadan soń birden token jaratıw
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def manage_profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
            return Response({"message": "Siz sistemadan tabıslı shıqtıńız"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Token nadurıs"}, status=status.HTTP_400_BAD_REQUEST)