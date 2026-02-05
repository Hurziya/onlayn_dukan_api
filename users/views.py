from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken



class UserViewSet(viewsets.ModelViewSet):
    """
    Paydalanıwshılardı dizimnen ótkeriw, profilin kórsetiw, jańalaw hám 
    sistemadan shıǵarıw (logout) processlerin basqarıw ushın ViewSet.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Action túrine qaray ruxsatlardı belgileydi."""
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get','patch'], url_path='me')
    def manage_profile(self, request):
        """
        Paydalanıwshı óz profilin kóriwi hám ózgertiwi ushın (/users/me/).
        ID kiritiliwi shárt emes, request.user-den avtomat alınadı.
        """
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """
        Refresh tokendi blacklistke qosıw arqılı paydalanıwshını sistemadan shıǵarıw.
        """
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token kiritilmegen"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist() 
            return Response({"message": "Siz sistemadan tabıslı shıqtıńız"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Token nadurıs yamasa aldın biykar etilgen"}, status=status.HTTP_400_BAD_REQUEST)

