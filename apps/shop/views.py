from django.views.generic import ListView,DetailView
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Product, ProductVariant, Order, OrderItem
from .forms import OrderForm
from .cart import Cart

# Create your views here.
class ProductListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related('photos', 'variants')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = Cart(self.request)
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related('photos', 'variants')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = Cart(self.request)
        return context


@require_POST
def cart_add(request):
    variant_id = request.POST.get('variant_id')
    if not variant_id:
        return render(request, 'shop/partials/cart_error.html', {'error': 'Выберите размер'})

    variant = get_object_or_404(ProductVariant, pk=variant_id)
    quantity = int(request.POST.get('quantity', 1))
    cart = Cart(request)
    cart.add(variant, quantity)
    return render(request, 'shop/partials/cart_button.html', {'cart': cart})


@require_POST
def cart_remove(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    cart = Cart(request)
    cart.remove(variant)
    return render(request, 'shop/partials/cart_detail.html', {'cart': cart})


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/partials/cart_detail.html', {'cart': cart})


def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        return render(request, 'shop/partials/cart_empty.html')

    cart_total = sum(item['variant'].product.price * item['quantity'] for item in cart)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    variant=item['variant'],
                    quantity=item['quantity'],
                )
            cart.clear()
            return render(request, 'shop/partials/order_success.html')
        return render(request, 'shop/partials/checkout_form.html',
                      {'form': form, 'cart': cart, 'cart_total': cart_total})

    form = OrderForm()
    return render(request, 'shop/partials/checkout_form.html', {'form': form, 'cart': cart, 'cart_total': cart_total})