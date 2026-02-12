from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, permissions, mixins, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Category, Product, Card, CardItem, Order, OrderItem, Review
# OrderItemSerializer-di importlarǵa qosıń (serializers.py-da jazǵan bolsańız)
from .serializers import (
    CategorySerializer, ProductSerializer, CardSerializer, 
    AddToCardSerializer, CheckoutSerializer, OrderSerializer, 
    ReviewSerializer
)

# --- CATEGORY VIEWSET ---
@extend_schema_view(
    list=extend_schema(tags=['Kategoriya'], summary="Barlıq bas kategoriyalar"),
)
class CategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer


# --- PRODUCT VIEWSET ---
@extend_schema_view(
    list=extend_schema(tags=['Ónimler'], summary="Ónimler dizimi hám filtr"),
    retrieve=extend_schema(tags=['Ónimler'], summary="Ónim haqqında tolıq maǵlıwmat"),
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer


# --- CARD VIEWSET ---
class CardViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CardSerializer

    @extend_schema(tags=['Sebet'], summary="Sebetti kóriw", responses=CardSerializer)
    @action(detail=False, methods=['get'])
    def my_card(self, request):
        card, _ = Card.objects.get_or_create(user=request.user)
        return Response(CardSerializer(card).data)

    @extend_schema(tags=['Sebet'], summary="Sebetke qosıw", request=AddToCardSerializer)
    @action(detail=False, methods=['post'])
    def add(self, request):
        ser = AddToCardSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        with transaction.atomic():
            prod = Product.objects.select_for_update().get(id=ser.validated_data['product_id'])
            cart, _ = Card.objects.get_or_create(user=request.user)
            item, _ = CardItem.objects.get_or_create(card=cart, product=prod)
            item.quantity = F('quantity') + ser.validated_data['quantity']
            item.save()
        return Response({"status": "Qosıldı"}, status=201)


# --- ORDER VIEWSET ---
class OrderViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.none()

    def get_queryset(self):
        
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    @extend_schema(tags=['Buyırtpa'], summary="Checkout (Buyırtpa beriw)", request=CheckoutSerializer)
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        ser = CheckoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        with transaction.atomic():
            items = CardItem.objects.filter(id__in=ser.validated_data['card_item_ids'], card__user=request.user)
            if not items: return Response({"error": "Bos"}, status=400)
            
            order = Order.objects.create(user=request.user, total_price=0, address=ser.validated_data['address'])
            total = 0
            for i in items:
                price = i.product.final_price
                total += price * i.quantity
                OrderItem.objects.create(order=order, product=i.product, price=price, quantity=i.quantity)
                Product.objects.filter(id=i.product.id).update(stock=F('stock') - i.quantity)
            
            order.total_price = total
            order.save()
            items.delete()
        
        # OrderItemSerializer-di OrderSerializer avtomat paydalanadı
        return Response(OrderSerializer(order).data)


# --- PERMISSIONS ---
class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


# --- REVIEW VIEWSET ---
@extend_schema_view(
    create=extend_schema(
        tags=['Pikirler'], 
        summary="Pikir qaldırıw",
        description="Tek usı ónimdi satıp alǵan hám tólemi 'PAID' yamasa 'SHIPPED' statusındaǵı adamlar pikir qaldıra aladı."
    ),
    list=extend_schema(tags=['Pikirler'], summary="Pikirler dizimi"),
    update=extend_schema(tags=['Pikirler'], summary="Pikirni ózgertiw (tek avtor)"),
    destroy=extend_schema(tags=['Pikirler'], summary="Pikirni óshiriw (tek avtor)"),
)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'product').all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data.get('product')

        has_purchased = OrderItem.objects.filter(
            order__user=user, 
            product=product, 
            order__status__in=['PAID', 'SHIPPED']
        ).exists()

        if not has_purchased:
            raise serializers.ValidationError({
                "detail": "Siz bul ónimdi satıp almaǵansız, sonlıqtan pikir qaldıra almaysız."
            })

        serializer.save(user=user)