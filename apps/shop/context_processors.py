from .cart import Cart
from .models import Product

def cart(request):
    return {'cart': Cart(request)}

def shop_has_products(request):
    return {
        'shop_has_products': Product.objects.filter(is_active=True).exists()
    }