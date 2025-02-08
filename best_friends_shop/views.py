from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import  CustomAuthenticationForm,CustomUserCreationForm,ProductForm,CategoryForm
from .models import Product, Category, Cart, CartItem
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test

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
                messages.success(request,"Successfully login")
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


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,defaults={'quantity': 1})
    cart_item.quantity += 1
    cart_item.save()

    return redirect('home')

# Cart Page View


def cart_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        cart=None
    cart_items = cart.cartitem_set.all()
    return render(request, 'cart.html', {'cart':cart,'cart_items': cart_items, 'total_price': cart.total_price() if cart else 0})

def is_admin(user):
    return user.is_staff 

@user_passes_test(is_admin)
def add_product(request):
    if  request.method=="POST":
        form=ProductForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"Product added successfully")
            return redirect("home")
        
    else:
        form=ProductForm()
    return render(request,'add_product.html',{'form':form})

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