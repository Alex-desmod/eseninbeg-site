from django.utils.text import slugify
from django.db import models

# Create your models here.
class Product(models.Model):
    TYPE_CHOICES = [
        ('tshirt', 'футболка'),
        ('longsleeve', 'лонгслив'),
        ('hoodie', 'худи'),
        ('socks', 'носки'),
        ('accessory', 'аксессуар'),
        ('other', 'другое'),
    ]

    slug = models.SlugField('URL', unique=True, blank=True)
    product_type = models.CharField('Тип', max_length=20, choices=TYPE_CHOICES)
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField('Доступен для заказа', default=True)
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        ordering = ['product_type', 'name']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    @property
    def total_stock(self):
        return sum(v.stock for v in self.variants.all())

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    SIZE_CHOICES = [
        ('XS', 'XS'), ('S', 'S'), ('M', 'M'),
        ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'),
        ('one_size', 'один размер'),
    ]

    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    size = models.CharField('Размер', max_length=10, choices=SIZE_CHOICES)
    stock = models.PositiveIntegerField('Остаток', default=0)

    class Meta:
        unique_together = [('product', 'size')]
        verbose_name = 'Вариант товара'
        verbose_name_plural = 'Варианты товара'

    def __str__(self):
        return f'{self.product.name} — {self.get_size_display()} ({self.stock} шт.)'


class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField('Фото', upload_to='shop/products/')
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Фото товара'
        verbose_name_plural = 'Фото товара'

    def __str__(self):
        return f'Фото {self.product.name} #{self.pk}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'новая'),
        ('confirmed', 'подтверждена'),
        ('cancelled', 'отменена'),
    ]

    full_name = models.CharField('ФИО', max_length=200)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email', blank=True)
    comment = models.TextField('Комментарий к заказу', blank=True)
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Дата заявки', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f'Заявка №{self.pk} — {self.full_name}'

    @property
    def total_price(self):
        return sum(item.variant.product.price * item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, related_name='order_items', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Позиция заявки'
        verbose_name_plural = 'Позиции заявки'

    def __str__(self):
        return f'{self.variant} × {self.quantity}'