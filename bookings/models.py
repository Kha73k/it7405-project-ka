from django.db import models
from django.contrib.auth.models import User

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return self.name

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    customer_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.service.name} on {self.appointment_date}"
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']

class Rating(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    RATING_TYPE_CHOICES = [
        ('overall', 'Overall Company'),
        ('service', 'Specific Service'),
    ]
    
    rating_type = models.CharField(max_length=20, choices=RATING_TYPE_CHOICES)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.rating_type == 'overall':
            return f"{self.customer_name} - Overall Rating: {self.rating} stars"
        return f"{self.customer_name} - {self.service.name}: {self.rating} stars"
    
    class Meta:
        ordering = ['-created_at']

        
class ProductCategory(models.Model):
    ''''idk'''
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Product Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    """Products available in the shop"""
    CATEGORY_CHOICES = [
        ('engine_oil', 'Engine Oil'),
        ('coolant', 'Coolant'),
        ('polish', 'Car Polish'),
        ('cleaning', 'Cleaning Supplies'),
        ('accessories', 'Accessories'),
        ('other', 'Other'),
    ]
    
    CAR_MAKE_CHOICES = [
        ('universal', 'Universal'),
        ('toyota', 'Toyota'),
        ('lexus', 'Lexus'),
        ('nissan', 'Nissan'),
        ('hyundai', 'Hyundai'),
        ('ford', 'Ford'),
        ('gmc', 'GMC'),
        ('bmw', 'BMW'),
        ('mercedes', 'Mercedes-Benz'),
        ('audi', 'Audi'),
        ('volkswagen', 'Volkswagen'),
        ('porsche', 'Porsche'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    car_make = models.CharField(max_length=50, choices=CAR_MAKE_CHOICES, default='universal')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=3)  # BHD format
    image_url = models.CharField(max_length=500, blank=True, help_text="Path to image in static folder (e.g., 'images/products/oil.jpg')")
    stock_quantity = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_car_make_display()}"

class Cart(models.Model):
    """Shopping cart for customers"""
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_total(self):
        total = sum(item.get_subtotal() for item in self.items.all())
        return round(total, 3)  # Round to 3 decimal places for BHD
    
    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    """Items in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def get_subtotal(self):
        # Convert to float for Djongo compatibility
        return float(self.product.price) * self.quantity
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class Order(models.Model):
    """Customer orders"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('card', 'Card on Delivery'),
        ('benefit', 'BenefitPay on Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    
    # Bahrain address fields
    house_number = models.CharField(max_length=50)
    road_number = models.CharField(max_length=50)
    block_number = models.CharField(max_length=50)
    area = models.CharField(max_length=100, help_text="e.g., Riffa, Manama, Muharraq")
    building_name = models.CharField(max_length=200, blank=True, help_text="Optional")
    flat_number = models.CharField(max_length=50, blank=True, help_text="Optional")
    additional_directions = models.TextField(blank=True)
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=3)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer_name}"
    
    def get_full_address(self):
        address_parts = [
            f"House {self.house_number}",
            f"Road {self.road_number}",
            f"Block {self.block_number}",
            self.area
        ]
        if self.building_name:
            address_parts.insert(0, self.building_name)
        if self.flat_number:
            address_parts.insert(1, f"Flat {self.flat_number}")
        return ", ".join(address_parts)

class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=3)
    
    def get_subtotal(self):
        # Convert to float for Djongo compatibility
        return float(self.price) * self.quantity
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name}"    



