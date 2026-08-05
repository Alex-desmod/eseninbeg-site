from django.contrib import admin
from .models import Product, ProductVariant, ProductPhoto, Order, OrderItem

# Register your models here.
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductPhotoInline(admin.TabularInline):
    model = ProductPhoto
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_type', 'is_active', 'total_stock']
    list_filter = ['product_type', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline, ProductPhotoInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['variant', 'quantity']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'status', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
    readonly_fields = ['created_at']
    inlines = [OrderItemInline]