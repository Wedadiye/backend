from django.shortcuts import render

# Create your views here.
"""
View for Shop Api.
"""
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartItemSerializer

from backend.models import (
    Category,
    Product,
    Order,
    OrderItem,
    CartItem
)
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    CartItemSerializer,
    OrderSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """View for managing categories."""
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('-name')

    def get_permissions(self):
        """Customize permission classes based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """Create a new category."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Update an existing category."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a category."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_exempt, name='dispatch')
class ProductViewSet(viewsets.ModelViewSet):
    """View for managing products."""
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Return products for the current authenticated user
          or all products."""
        if self.request.user.is_authenticated:
            return Product.objects.filter(user=self.request.user)
        return Product.objects.all()




    def list_products_by_category(self, request, category_id):
        """List products associated with a specific category."""
        queryset = Product.objects.filter(category=category_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def perform_create(self, serializer):
        """Create a new product."""
        serializer.save(user=self.request.user)


    def update(self, request, *args, **kwargs):
        product = Product.objects.filter(pk=kwargs['pk']).first()
        if product and product.user != request.user:
            return Response(
                {'detail': 'Not authorized to update this product.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        product = Product.objects.filter(pk=kwargs['pk']).first()
        if product and product.user != request.user:
            return Response(
                {'detail': 'Not authorized to delete this product.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)



class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    
    @action(detail=False, methods=['get'])
    def get_cart_items(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(cart__user=user)

        cart_items_data = []
        for cart_item in cart_items:
            product_data = ProductSerializer(cart_item.product).data
            cart_items_data.append({
                'product_id': product_data['id'],
                'name': product_data['name'],
                'quantity': cart_item.quantity,
                'price': product_data['price'],
                'stock': product_data['stock']

            })

        return Response(cart_items_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        user = request.user
        product_id = request.data.get('product_id')

        # Vérifier si l'utilisateur a un panier
        if not hasattr(user, 'cart'):
            # Si l'utilisateur n'a pas de panier, créer un nouveau panier pour cet utilisateur
            Cart.objects.create(user=user)

        # Récupérer le panier de l'utilisateur
        cart = user.cart
        # Vérifier si le produit existe déjà dans le panier de l'utilisateur
        cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()

        if cart_item:
            # Si le produit existe, mettre à jour la quantité
            cart_item.quantity += 1
            cart_item.save()
        else:
            # Si le produit n'existe pas, créer une nouvelle entrée dans le panier
            CartItem.objects.create(cart=user.cart, product_id=product_id)

        return Response(status=status.HTTP_201_CREATED)
  


    # Vos autres actions ici...

    @action(detail=False, methods=['put'])
    def update_quantity(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        new_quantity = request.data.get('quantity')

        try:
            # Récupérer le panier de l'utilisateur
            cart = user.cart
            # Récupérer l'article du panier à mettre à jour
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            # Mettre à jour la quantité
            cart_item.quantity = new_quantity
            cart_item.save()
            return Response(status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cet article n\'existe pas dans votre panier'}, status=status.HTTP_404_NOT_FOUND)
    
    
    @action(detail=False, methods=['delete'])
    def delete_from_cart(self, request):
        user = request.user
        product_id = request.data.get('product_id')

        try:
            cart_item = CartItem.objects.get(cart__user=user, product_id=product_id)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cet article n\'existe pas dans votre panier'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['delete'])
    def clear_cart(self, request):
        user = request.user
        cart_items = CartItem.objects.filter(cart__user=user)
        
        if cart_items.exists():
            cart_items.delete()
            return Response({'message': 'Le panier a été vidé avec succès.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'Le panier est déjà vide.'}, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    """Viewset for managing orders."""
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        products_data = serializer.validated_data.pop('products')
        order = serializer.save(user=self.request.user)

        for product_data in products_data:
            product = product_data['product']

            # Check if product is a Product instance
            # and extract ID if necessary
            if isinstance(product, Product):
                product_id = product.id
            else:
                product_id = product

            quantity = product_data['quantity']

            # Now retrieve the product using the ID
            product_instance = Product.objects.get(id=product_id)

            if quantity > product_instance.stock:
                raise ValidationError(
                    f'Insufficient stock for product ID {product_id}.'
                )

            OrderItem.objects.create(
                order=order,
                product=product_instance,
                quantity=quantity
            )

            # Update product stock
            product_instance.stock -= quantity
            product_instance.save()
    
    # pour tester dans postman :GET http://localhost:8000/commande/
    
    def get_queryset(self):
        """Retrieve orders for the current authenticated user."""
        return Order.objects.filter(user=self.request.user)
    
    
    @action(detail=False, methods=['get'])
    def order_details(self, request):
      orders = Order.objects.all()  # Récupère toutes les commandes
      data = []
      for order in orders:
        order_data = {
            'user': order.user.email,
            'address': order.address,
            'pays': order.pays,
            'total': order.total,
            'items': []
        }
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            order_item_data = {
                'product_name': item.product.name,
                'quantity': item.quantity
            }
            order_data['items'].append(order_item_data)
            data.append(order_data)
        return Response(data)
        
    
    @action(detail=False, methods=['get'])
    def order_details(self, request):
      orders = Order.objects.all()  # Récupère toutes les commandes
      data = []
      for order in orders:
        order_data = {
            'user': order.user.email,
            'address': order.address,
            'pays': order.pays,
            'total': order.total,
            'items': []
        }
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            order_item_data = {
                'product_name': item.product.name,
                'quantity': item.quantity
            }
            order_data['items'].append(order_item_data)
        data.append(order_data)  # Déplacez cette ligne à l'intérieur de la boucle for order in orders
      return Response(data)  # Déplacez cette ligne à l'extérieur de la boucle for order in orders

    
    