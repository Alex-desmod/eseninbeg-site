from .models import ProductVariant

CART_SESSION_KEY = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, variant, quantity=1):
        variant_id = str(variant.id)
        self.cart[variant_id] = self.cart.get(variant_id, 0) + quantity
        self._save()

    def remove(self, variant):
        variant_id = str(variant.id)
        if variant_id in self.cart:
            del self.cart[variant_id]
            self._save()

    def update(self, variant, quantity):
        variant_id = str(variant.id)
        if quantity <= 0:
            self.remove(variant)
        else:
            self.cart[variant_id] = quantity
            self._save()

    def clear(self):
        self.cart.clear()
        self._save()

    def _save(self):
        self.session.modified = True

    def __iter__(self):
        variants = ProductVariant.objects.filter(
            id__in=self.cart.keys()
        ).select_related('product')
        variants_by_id = {str(v.id): v for v in variants}

        for variant_id, quantity in self.cart.items():
            variant = variants_by_id.get(variant_id)
            if variant:
                yield {'variant': variant, 'quantity': quantity}

    def __len__(self):
        return sum(self.cart.values())