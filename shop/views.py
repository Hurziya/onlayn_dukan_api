from django.db import transaction
from rest_framework import viewsets, status, filters, permissions, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets

from .models import Category, Product, Card, CardItem, Order, OrderItem, Review
from .serializers import (CardSerializer, ProductSerializer, OrderSerializer, ReviewSerializer, CategorySerializer)
  


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Tek avtorǵa ózgeris kirgiziwge ruxsat beriw. 
    Basqalar tek kóre aladı (Read Only).
    """
    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS sorawlarına barlıqqa ruxsat
        if request.method in permissions.SAFE_METHODS:
            return True
        # Ózgertiw (PUT, PATCH, DELETE) tek avtor ushın
        return obj.user == request.user
    

# 1. PAGINATION
class StandardResultsSetPagination(PageNumberPagination):
    """
    Ónimler hám buyırtpalar dizimin betlerge bólip kórsetiw ushın standart klass.
    Standart halda 10 dana element shıǵaradı.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100



class CategoryViewSet(mixins.ListModelMixin,      # Tek GET /categories/ (Dizim)
                      mixins.CreateModelMixin,    # Tek POST /categories/ (Qosıw)
                      viewsets.GenericViewSet):   # Tiykarǵı klass
    """
    Kategoriyalarda ID boyınsha hesh qanday metod joq.
    Swagger-de tek GET (list) hám POST (create) qaladı.
    """
    queryset = Category.objects.all().order_by('id') 
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = None
    search_fields = ['name']

    def get_queryset(self):
        # Filtrlew logikası ózgermeydi
        queryset = Category.objects.all().order_by('id')
        parent_id = self.request.query_params.get('parent')
        
        if parent_id:
            if parent_id == 'null':
                return queryset.filter(parent__isnull=True)
            return queryset.filter(parent_id=parent_id)
        
        return queryset.filter(parent__isnull=True)

    def get_permissions(self):
        # Tek eki action qaldı: list hám create
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


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
        if self.action == 'add_review': # Usı qatardı qosıń
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_review(self, request, pk=None):
        product = self.get_object()
        # Bir paydalanıwshı bir ónimge tek bir márte pikir qaldıra alatuǵın qılıw (itimal talap)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            # user=request.user — bul jerde avtor tayınlanadı
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

        user_card, _ = Card.objects.get_or_create(user=request.user)
        item, created = CardItem.objects.get_or_create(card=user_card, product=product, defaults={'quantity': 0})

        if product.stock < (item.quantity + quantity):
            return Response({"error": f"Qoymada jetkilikli ónim joq. Barı: {product.stock}"}, status=400)

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
    


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)