from django.db import transaction
from rest_framework import viewsets, status, filters, permissions, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets

from .models import Category, Product, Card, CardItem, Order, OrderItem, Review
from .serializers import (CardSerializer, ProductSerializer, OrderSerializer, ReviewSerializer, CategorySerializer, AddToCardSerializer, CheckoutSerializer)
  


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
        # Tek eki action list hám create
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
        if self.action == 'add_review':
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

    @extend_schema(
        request=AddToCardSerializer, 
        responses={201: None},
        description="Ónimniń ID-si hám sanı arqılı sebetke element qosıw."
    )
    @action(detail=False, methods=['post'], url_path='add')
    def add_to_card(self, request):
        serializer = AddToCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
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
    Buyırtpalardı basqarıw viewseti.
    Checkout arqalı sebetińizdi buyırtpaǵa aylandıra alasız.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Tiykarǵı POST /orders/ metodın japsańız boladı yamasa userdi avtomat qosıń
        serializer.save(user=self.request.user)

    @extend_schema(
        request=CheckoutSerializer,
        responses={201: OrderSerializer},
        description="Sebettegi tovarlardı buyırtpa retinde rásmiylestiriw (Checkout)."
    )
    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        checkout_serializer = CheckoutSerializer(data=request.data)
        checkout_serializer.is_valid(raise_exception=True)
        
        address = checkout_serializer.validated_data.get('address') or request.user.address
        
        if not address:
            return Response(
                {"error": "Mánzil kiritiliwi shárt yamasa profilińizde mánzil kórsetilgen bolıwı kerek."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Sebeti bar ekenin tekseriw
        user_card = Card.objects.filter(user=request.user).first()
        if not user_card or not user_card.items.exists():
            return Response({"error": "Sebetińiz bos. Buyırtpa beriw ushın dáslep ónim qosıń."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Buyırtpa jaratıw 
        try:
            with transaction.atomic():
                # Buyırtpa ob'ektin jaratıw
                order = Order.objects.create(
                    user=request.user, 
                    total_price=0, 
                    address=address
                )
                
                total_sum = 0
                
                # Sebet elementlerin aylanıp shıǵıw
                for item in user_card.items.all():
                    # select_for_update() — maǵlıwmatlar bazasında usı tovardı "block" qılıp turadı
                    product = Product.objects.select_for_update().get(id=item.product.id)

                    # Qoymada bar ekenin tekseriw
                    if product.stock < item.quantity:
                        raise serializers.ValidationError(
                            f"Keshiresiz, '{product.name}' óniminen qoymada jetkilikli emes. Barı: {product.stock}"
                        )

                    current_price = product.discount_price if product.discount_price else product.price
                    
                    # OrderItem jaratıw
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price=current_price
                    )

                    # Esap-kitap hám stocktı jańalaw
                    total_sum += current_price * item.quantity
                    product.stock -= item.quantity
                    product.save()

                # Buyırtpa ulıwma bahasın saqlaw
                order.total_price = total_sum
                order.save()

                # Sebeti tazalaw
                user_card.items.all().delete()

            # Juwaptı qaytarıw
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Sistema qáteligi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)