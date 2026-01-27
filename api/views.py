from django.db import transaction
from rest_framework import viewsets, status, filters, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Category, Product, Card, CardItem, Order, OrderItem, User
from .serializers import *

# 1. PAGINATION
class StandardResultsSetPagination(PageNumberPagination):
    """
    Ónimler hám buyırtpalar dizimin betlerge bólip kórsetiw ushın standart klass.
    Standart halda 10 dana element shıǵaradı.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# 2. USER VIEWSET
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

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
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


# 3. CATEGORY VIEWSET
class CategoryViewSet(viewsets.ModelViewSet):
    """
    Kategoriyalardı basqarıw. Kategoriyalar hámmege ashıq, 
    biraq tek Adminler Qosa yamasa ózgerte aladı.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        queryset = Category.objects.all()
        
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            if parent_id == 'null':
                return queryset.filter(parent__isnull=True)
            return queryset.filter(parent_id=parent_id)
        else:
            return queryset.filter(parent__isnull=True)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
   


    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Anıq bir kategoriyaǵa tiyisli barlıq aktiv ónimler dizimin qaytaradı.
        """
        category = self.get_object()
        products = Product.objects.filter(category=category, is_active=True)
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, request)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
    
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


# 4. PRODUCT VIEWSET
class ProductViewSet(viewsets.ModelViewSet):
    """
    Ónimler dizimin kórsetiw, izlew hám bahası boyınsha filtrlew ushın.
    
    """
    queryset = Product.objects.filter(is_active=True).order_by('id')
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = {
        'category': ['exact'],
        'price': ['gte', 'lte'], 
    }
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    

    # pikir qaldiriw ushin qosimsha endopoind
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_review(self, request, pk=None):
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 5. CARD VIEWSET
class CardViewSet(viewsets.ModelViewSet):
    """
    Paydalanıwshınıń jeke sebetin basqarıw. 
    Ónim qosıw hám sebetten elementlerdi óshiriw logikasın óz ishine aladı.
    """
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Tek login bolǵan paydalanıwshınıń óz sebetin qaytaradı."""
        return Card.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='add')
    def add_to_card(self, request):
        """
        Ónimniń ID-si hám sanı arqılı sebetke element qosıw.
        Ónimniń stock (qoymadaǵı sanı) jetkilikliligi tekseriledi.
        """
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"error": "Ónim tabılmadı"}, status=status.HTTP_404_NOT_FOUND)

        if product.stock < quantity:
            return Response({"error": f"Qoymada jetkilikli ónim joq. Barı: {product.stock}"}, 
                            status=status.HTTP_400_BAD_REQUEST)

        user_card, _ = Card.objects.get_or_create(user=request.user)
        item, created = CardItem.objects.get_or_create(card=user_card, product=product, 
                                                       defaults={'quantity': quantity})
        if not created:
            item.quantity += quantity
            item.save()

        return Response({"message": "Tovar sebetke qosıldı"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='remove')
    def remove_item(self, request, pk=None):
        """
        Sebetten anıq bir elementti óshiriw (DELETE /card/{item_id}/remove/).
        """
        try:
            item = CardItem.objects.get(id=pk, card__user=request.user)
            item.delete()
            return Response({"message": "Ónim sebetten óshirildi"}, status=status.HTTP_204_NO_CONTENT)
        except CardItem.DoesNotExist:
            return Response({"error": "Bunday element sebetińizde tabılmadı"}, status=status.HTTP_404_NOT_FOUND)


# 6. ORDER VIEWSET
class OrderViewSet(viewsets.ModelViewSet):
    """
    Buyırtpalar tariyxın kóriw hám sebetten buyırtpa jaratıw (checkout).
    Checkout waqtında stock kemeytiledi hám sebet tazalanadı.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Paydalanıwshı tek ózi bergen buyırtpalar dizimin kóre aladı."""
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """
        Sebettegi ónimlerdi buyırtpaǵa aylandırıw.
        Tranzakciya qollanılǵan: qátelik bolsa barlıq ózgerisler biykar etiledi.
        """
        user_card = Card.objects.filter(user=request.user).first()
        
        if not user_card or not user_card.items.exists():
            return Response({"error": "Sebetińiz bos"}, status=status.HTTP_400_BAD_REQUEST)
        
        address = request.data.get('address') or request.user.address
        if not address:
            return Response({"error": "Mánzil kórsetiliwi shárt"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            total_sum = 0
            order = Order.objects.create(user=request.user, total_price=0, address=address)

            for item in user_card.items.all():
                product = Product.objects.select_for_update().get(id=item.product.id)

                if product.stock < item.quantity:
                    raise serializers.ValidationError(f"{product.name} qoymada jetkilikli emes")

                price = product.discount_price or product.price
                OrderItem.objects.create(
                    order=order, product=product, 
                    quantity=item.quantity, price=price
                )
                
                total_sum += price * item.quantity
                product.stock -= item.quantity
                product.save()

            order.total_price = total_sum
            order.save()
            user_card.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        """Standart create metodı jawılǵan, buyırtpa ushın checkout isletiliwi kerek."""
        return Response({"error": "Buyırtpa ushın /checkout/ isletin"}, 
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)
   