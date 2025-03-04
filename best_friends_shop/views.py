from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomAuthenticationForm, CustomUserCreationForm, ProductForm, CategoryForm
from .models import Product, Category, Cart, CartItem, Order
from django.contrib import messages
# from django.utils.safestring import mark_safe
# from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
import time
# Home Page View


def home(request):
    products = Product.objects.all()

    return render(request, 'home.html', {
        'products': products,
        'user_authenticated': request.user.is_authenticated,
        'is_admin': request.user.is_staff
    })


# Login View

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Successfully login")
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


# Registration View

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            messages.success(request, 'Registration successful.')
            return redirect('login')
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Add to Cart View


# def add_to_cart(request, product_id):
#     if not request.user.is_authenticated:
#         return redirect('login')

#     product = Product.objects.get(id=product_id)
#     cart, created = Cart.objects.get_or_create(user=request.user)

#     cart_item, created = CartItem.objects.get_or_create(
#         cart=cart, product=product, defaults={'quantity': 1})
#     cart_item.quantity += 1
#     cart_item.save()

#     return redirect('home')

# # Cart Page View


# def cart_view(request):
#     if not request.user.is_authenticated:
#         return redirect('login')
#     try:
#         cart = Cart.objects.get(user=request.user)
#     except Cart.DoesNotExist:
#         cart = None
#     cart_items = cart.cartitem_set.all()
#     return render(request, 'cart.html', {'cart': cart, 'cart_items': cart_items, 'total_price': cart.total_price() if cart else 0})

stripe.api_key = settings.STRIPE_SECRET_KEY
@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={'quantity': 1})
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart_view')

@login_required
def cart_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cartitem_set.all()
        total_price = sum(item.product.price * item.quantity for item in cart_items)
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
        total_price = 0
        
    storage = messages.get_messages(request)
    storage.used = True

    return render(request, 'cart.html', {'cart': cart, 'cart_items': cart_items, 'total_price': total_price})

@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'Best Friend Shop Purchase'},
                        'unit_amount': int(total_price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/cancel/'),
            )
            return redirect(session.url)
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
            return redirect('checkout')

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})

def success_view(request):
    messages.success(request, "Payment successful! Your order has been placed.")
    return render(request, 'success.html')

def cancel_view(request):
    messages.error(request, "Payment was canceled. Please try again.")
    return render(request, 'cancel.html')


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully")
            return redirect("home")

    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect('add_category')
    else:
        form = CategoryForm()

    messages.get_messages(request).used = True
    return render(request, 'add_category.html', {'form': form})
