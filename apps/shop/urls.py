from django.urls import path
from .views import ProductListView, cart_add, cart_remove, cart_detail, checkout, ProductDetailView

app_name = 'shop'

urlpatterns = [
    path('cart/add/', cart_add, name='cart_add'),
    path('cart/remove/<int:variant_id>/', cart_remove, name='cart_remove'),
    path('cart/', cart_detail, name='cart_detail'),
    path('checkout/', checkout, name='checkout'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='detail'),
    path('', ProductListView.as_view(), name='catalog'),
]