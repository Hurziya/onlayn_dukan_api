from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, permissions, mixins, serializers, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .models import Category, Product, Card, CardItem, Order, OrderItem, Review
from .serializers import (
    CategorySerializer, ProductSerializer, CardSerializer, 
    AddToCardSerializer, CheckoutSerializer, OrderSerializer, 
    ReviewSerializer
)


@extend_schema_view(
    list=extend_schema(tags=['Kategoriya'], summary="Barlıq bas kategoriyalar"),
)
class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'slug']

    def get_queryset(self):
        base_query = Category.objects.all() if self.request.user.is_staff else Category.objects.filter(is_active=True)
        if self.action == 'list':
            return base_query.filter(parent__isnull=True)
        return base_query

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        category_ids = list(instance.children.values_list('id', flat=True)) + [instance.id]
        
        products = Product.objects.filter(category_id__in=category_ids, is_active=True)
        
        category_data = self.get_serializer(instance).data
        product_data = ProductSerializer(products, many=True, context={'request': request}).data
        
        return Response({
            "category": category_data,
            "products": product_data
        })


@extend_schema_view(
        list=extend_schema(tags=['Ónimler'],summary="Ónimler dizimi hám filtr",
        parameters=[OpenApiParameter(
            name='category',
            description='Kategoriya ID boyınsha filtr (ishkilerin qosıp)',
            required=False,
            type=int
            ),]
        ),
        retrieve=extend_schema(tags=['Ónimler'], summary="Ónim haqqında tolıq maǵlıwmat"),
        )
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [
    filters.SearchFilter,
    DjangoFilterBackend,
    filters.OrderingFilter,
    ]
    search_fields = ["name"]
    ordering_fields = ["price", "name"]
    ordering = ["-price"]
    http_method_names = ['get']



@extend_schema_view(
    list=extend_schema(tags=['Ónimler'], summary="Ónimler dizimi hám filtr"),
    retrieve=extend_schema(tags=['Ónimler'], summary="Ónim haqqında tolıq maǵlıwmat"),
)
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related("category")
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    ordering_fields = ["price", "name",]
    ordering = ["-price"]
    http_method_names = ['get']

class CardViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CardSerializer
    pagination_class = None

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
        # sebetke qosıw
        with transaction.atomic():
            prod = Product.objects.select_for_update().get(id=ser.validated_data['product_id'])
            cart, _ = Card.objects.get_or_create(user=request.user)
            item, _ = CardItem.objects.get_or_create(card=cart, product=prod)
            item.quantity = F('quantity') + ser.validated_data['quantity']
            item.save()
        return Response({"status": "Qosıldı"}, status=201)



class OrderViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    @extend_schema(tags=['Zakazlar'], summary="Zakaz qılıw", request=CheckoutSerializer, responses={201: OrderSerializer})
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        user = request.user
        ser = CheckoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        
        address = ser.validated_data.get("address")
        card_item_ids = ser.validated_data.get("card_item_ids") 

        cart = get_object_or_404(Card, user=user)

        with transaction.atomic():
            if card_item_ids:
                items = cart.items.select_related('product').select_for_update().filter(id__in=card_item_ids) 
                
                if items.count() != len(card_item_ids):
                    return Response(
                        {"error": "Ayırım ónimler tabılmadı yamasa sizge tiyisli emes"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                items = cart.items.select_related('product').select_for_update().all()

            if not items.exists():
                return Response({"error": "Sebet bos!"}, status=status.HTTP_400_BAD_REQUEST)

            total_price = 0
            for i in items:
                if i.product.stock < i.quantity:
                    return Response(
                        {"error": f"{i.product.name} bazada jetkiliksiz!"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                total_price += i.product.final_price * i.quantity

            # Zakaz jaratıw
            order = Order.objects.create(
                user=user, 
                total_price=total_price, 
                address=address,
                status="PENDING" 
            )
            for i in items:
                OrderItem.objects.create(
                    order=order,
                    product=i.product,
                    quantity=i.quantity,
                    price=i.product.final_price
                )
            # Sebettegi ónimderdi azaytw
                Product.objects.filter(id=i.product.id).update(stock=F('stock') - i.quantity)

            items.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


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