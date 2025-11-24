from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Service, Appointment, Rating, Product, Cart, CartItem, Order, OrderItem
from .forms import RatingForm
import uuid

# Existing Views
def home(request):
    services = Service.objects.all()
    return render(request, 'bookings/home.html', {'services': services})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'bookings/register.html', {'form': form})

@login_required
def book_appointment(request, service_id):
    service = Service.objects.get(id=service_id)
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        customer_notes = request.POST.get('customer_notes', '')
        
        Appointment.objects.create(
            user=request.user,
            service=service,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            customer_notes=customer_notes
        )
        messages.success(request, f'Appointment for {service.name} booked successfully!')
        return redirect('my_appointments')
    
    return render(request, 'bookings/book_appointment.html', {'service': service})

@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'bookings/my_appointments.html', {'appointments': appointments})

# Rating Views
def reviews(request):
    """Display all reviews page"""
    overall_ratings = Rating.objects.filter(rating_type='overall')
    service_ratings = Rating.objects.filter(rating_type='service').select_related('service')
    
    # Calculate overall company average (simpler way)
    overall_count = overall_ratings.count()
    if overall_count > 0:
        total = sum(r.rating for r in overall_ratings)
        overall_avg = total / overall_count
    else:
        overall_avg = None
    
    # Get all services
    services = Service.objects.all()
    services_with_ratings = []
    
    for service in services:
        service_rating_list = Rating.objects.filter(rating_type='service', service=service)
        rating_count = service_rating_list.count()
        if rating_count > 0:
            avg_rating = sum(r.rating for r in service_rating_list) / rating_count
        else:
            avg_rating = None
        
        services_with_ratings.append({
            'name': service.name,
            'avg_rating': avg_rating,
            'rating_count': rating_count
        })
    
    context = {
        'overall_ratings': overall_ratings,
        'service_ratings': service_ratings,
        'overall_avg': overall_avg,
        'overall_count': overall_count,
        'services_with_ratings': services_with_ratings,
    }
    return render(request, 'bookings/reviews.html', context)

def submit_rating(request):
    """Submit a new rating"""
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('reviews')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RatingForm()
    
    return render(request, 'bookings/submit_rating.html', {'form': form})

# Shop Views
def shop(request):
    """Display all products"""
    from bookings.models import Product
    
    category = request.GET.get('category', '')
    car_make = request.GET.get('car_make', '')
    
    try:
        # Get all products
        all_products = Product.objects.all()
        products = []
        
        # Manual filtering to avoid Djongo issues
        for p in all_products:
            if not p.is_available:
                continue
            
            # Filter by category if specified
            if category and p.category != category:
                continue
            
            # Filter by car make if specified
            if car_make and p.car_make != car_make:
                continue
            
            products.append(p)
        
        print(f"Found {len(products)} products")
        
    except Exception as e:
        print(f"Error: {e}")
        products = []
    
    categories = Product.CATEGORY_CHOICES
    car_makes = Product.CAR_MAKE_CHOICES
    
    context = {
        'products': products,
        'categories': categories,
        'car_makes': car_makes,
        'selected_category': category,
        'selected_car_make': car_make,
    }
    return render(request, 'bookings/shop.html', context)

def get_or_create_cart(request):
    """Get or create a cart for the current session"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    cart, created = Cart.objects.get_or_create(session_id=session_key)
    return cart

@require_POST
def add_to_cart(request, product_id):
    """Add a product to cart"""
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    
    quantity = int(request.POST.get('quantity', 1))
    
    # Check if product already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'cart_count': cart.get_item_count(),
        'message': f'{product.name} added to cart!'
    })

def view_cart(request):
    """View shopping cart"""
    try:
        cart = get_or_create_cart(request)
        cart_items = list(cart.items.all())
        
        # Process items to handle Decimal128
        processed_items = []
        total = 0
        total_count = 0
        
        for item in cart_items:
            try:
                # Handle Djongo's Decimal128 type
                price_value = item.product.price
                
                # Convert Decimal128 to float
                if hasattr(price_value, 'to_decimal'):
                    price = float(price_value.to_decimal())
                elif isinstance(price_value, str):
                    price = float(price_value)
                else:
                    price = float(str(price_value))
                
                subtotal = price * item.quantity
                
                # Create a simple object to hold processed data
                class ProcessedItem:
                    def __init__(self, cart_item, calculated_price, calculated_subtotal):
                        self.id = cart_item.id
                        self.product = cart_item.product
                        self.quantity = cart_item.quantity
                        self.price = round(calculated_price, 3)
                        self.get_total_price = round(calculated_subtotal, 3)
                
                processed_item = ProcessedItem(item, price, subtotal)
                processed_items.append(processed_item)
                
                total += subtotal
                total_count += item.quantity
                
            except Exception as e:
                print(f"Error processing item: {e}")
                continue
        
        context = {
            'cart_items': processed_items,
            'total': round(total, 3),
            'cart_count': total_count
        }
        
    except Exception as e:
        print(f"Cart error: {e}")
        context = {
            'cart_items': [],
            'total': 0,
            'cart_count': 0
        }
    
    return render(request, 'bookings/cart.html', context)


@require_POST
def update_cart(request, product_id):  # Changed from item_id to product_id
    """Update cart item quantity"""
    cart = get_or_create_cart(request)
    
    # Find cart item by product_id instead
    try:
        product = get_object_or_404(Product, id=product_id)
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})
    
    action = request.POST.get('action')
    
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Updated {product.name} quantity')
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, f'Updated {product.name} quantity')
        else:
            cart_item.delete()
            messages.success(request, f'Removed {product.name} from cart')
    elif action == 'remove':
        cart_item.delete()
        messages.success(request, f'Removed {product.name} from cart')
    
    # Redirect back to cart page instead of JSON response
    return redirect('view_cart')

def checkout(request):
    """Checkout page"""
    cart = get_or_create_cart(request)
    
    if request.method == 'POST':
        # Create order
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate total manually with Decimal128 handling
        cart_items = list(cart.items.all())
        total = 0
        
        for item in cart_items:
            price_value = item.product.price
            if hasattr(price_value, 'to_decimal'):
                price = float(price_value.to_decimal())
            else:
                price = float(str(price_value))
            total += price * item.quantity
        
        order = Order.objects.create(
            order_number=order_number,
            customer_name=request.POST.get('name'),  # Changed from 'customer_name'
            customer_phone=request.POST.get('phone'),  # Changed from 'customer_phone'
            customer_email=request.POST.get('email', ''),  # Changed from 'customer_email'
            house_number=request.POST.get('house_number', ''),
            road_number=request.POST.get('road_number', ''),
            block_number=request.POST.get('block_number', ''),
            area=request.POST.get('area', ''),
            building_name=request.POST.get('building_name', ''),
            flat_number=request.POST.get('flat_number', ''),
            additional_directions=request.POST.get('notes', ''),  # Changed from 'additional_directions'
            payment_method=request.POST.get('payment_method', 'cash_on_delivery'),
            total_amount=round(total, 3),
            status='confirmed'
        )
        
        # Create order items
        for cart_item in cart_items:
            price_value = cart_item.product.price
            if hasattr(price_value, 'to_decimal'):
                price = float(price_value.to_decimal())
            else:
                price = float(str(price_value))
            
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                price=price
            )
        
        # Clear cart
        cart.items.all().delete()
        
        return redirect('order_confirmation', order_number=order.order_number)
    
    # GET request - show checkout form
    cart_items = list(cart.items.all())
    
    # Process items for display
    processed_items = []
    total = 0
    
    for item in cart_items:
        price_value = item.product.price
        if hasattr(price_value, 'to_decimal'):
            price = float(price_value.to_decimal())
        else:
            price = float(str(price_value))
        
        subtotal = price * item.quantity
        
        # Create a dict that mimics the CartItem object with extra data
        processed_item = {
            'product': item.product,
            'quantity': item.quantity,
            'price': price,
            'get_total_price': round(subtotal, 3)  # This matches the template
        }
        processed_items.append(processed_item)
        
        total += subtotal
    
    context = {
        'cart_items': processed_items,
        'total': round(total, 3),  # Changed from 'cart_total' to match template
        'cart_count': sum(item['quantity'] for item in processed_items)
    }
    return render(request, 'bookings/checkout.html', context)

def order_confirmation(request, order_number):
    """Order confirmation page"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Process order items to handle Decimal128
    order_items = []
    for item in order.items.all():
        price_value = item.price
        if hasattr(price_value, 'to_decimal'):
            price = float(price_value.to_decimal())
        else:
            price = float(str(price_value))
        
        subtotal = price * item.quantity
        
        order_items.append({
            'product_name': item.product_name,
            'quantity': item.quantity,
            'price': price,
            'subtotal': round(subtotal, 3)
        })
    
    # Handle total_amount
    total_value = order.total_amount
    if hasattr(total_value, 'to_decimal'):
        total_amount = float(total_value.to_decimal())
    else:
        total_amount = float(str(total_value))
    
    context = {
        'order': order,
        'order_items': order_items,
        'total_amount': round(total_amount, 3)
    }
    return render(request, 'bookings/order_confirmation.html', context)

def booking(request):
    services = Service.objects.all()
    return render(request, 'bookings/booking.html', {'services': services})