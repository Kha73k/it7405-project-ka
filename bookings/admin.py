from django.contrib import admin
from .models import (
    Service, Appointment, Rating, 
    ProductCategory, Product, Cart, CartItem, Order, OrderItem
)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_minutes']
    search_fields = ['name']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date']
    search_fields = ['user__username', 'service__name']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'rating_type', 'service', 'rating', 'created_at']
    list_filter = ['rating_type', 'rating', 'created_at']
    search_fields = ['customer_name']

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'car_make', 'price', 'stock_quantity', 'is_available']
    list_filter = ['category', 'car_make', 'is_available']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock_quantity', 'is_available']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'created_at', 'get_item_count']
    readonly_fields = ['session_id', 'created_at', 'updated_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'get_subtotal']
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'customer_phone', 'area', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'area', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'price', 'get_subtotal']