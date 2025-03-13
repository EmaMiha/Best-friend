from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import CustomAuthenticationForm, ProductForm, CategoryForm, SubCategoryForm, RegisterForm
from .models import Product, Category, Cart, CartItem, Order, OrderItem, SubCategory
from django.core.paginator import Paginator
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Sum



def home(request):
    
    products = Product.objects.all()
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    top_selling_products = get_top_selling_products()

    visits = request.session.get('visits', 0)
    request.session['visits'] = visits + 1

    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)

    selected_categories = request.GET.getlist('category')
    if selected_categories:
        products = products.filter(category__id__in=selected_categories)

    selected_subcategories = request.GET.getlist('subcategory')
    if selected_subcategories:
        products = products.filter(subcategory__id__in=selected_subcategories)


    sort_order = request.GET.get('sort')
    if sort_order == 'asc':
        products = products.order_by('price')
    elif sort_order == 'desc':
        products = products.order_by('-price')

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {
        'products': page_obj,
        'categories': categories,
        'subcategories': subcategories,
        'selected_categories': selected_categories,
        'selected_subcategories': selected_subcategories,
        "top_selling_products": top_selling_products
    })



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

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]

            if User.objects.filter(username=username).exists():
                messages.error(request, "This username is already taken. Please choose another one.")
                return render(request, "register.html", {"form": form})

            if User.objects.filter(email=email).exists():
                messages.error(request, "This email is already in use. Please use a different email.")
                return render(request, "register.html", {"form": form})

            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])  
            user.save()

            messages.success(request, "Registration successful! You can now log in.")
            return redirect("login")

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})

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
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "increase":
            cart_item.quantity += 1
        elif action == "decrease" and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()

    return redirect("cart_view")

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect("cart_view")

@login_required
def cart_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cartitem_set.all()
        for item in cart_items:
            item.total_price = item.quantity * item.product.price
        total_price = sum(item.total_price for item in cart_items)
    except Cart.DoesNotExist:
        cart_items = []
        total_price = 0

    return render(request, "cart.html", {"cart_items": cart_items, "total_price": total_price})

@login_required
def create_checkout_session(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if not cart_items:
        messages.error(request, "Your cart is empty!")
        return redirect('home')

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': item.product.name},
                    'unit_amount': int(item.product.price * 100),  
                },
                'quantity': item.quantity,
            }
            for item in cart_items
        ],
        mode='payment',
        success_url=request.build_absolute_uri('/success/'),
        cancel_url=request.build_absolute_uri('/cancel/'),
    )
    order = Order.objects.create(user=request.user, total_price=total_price, stripe_payment_id=session.id)

    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

    cart.cartitem_set.all().delete() 

    return redirect(session.url)  


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
        category_form = CategoryForm(request.POST)
        subcategory_form = SubCategoryForm(request.POST)

        if category_form.is_valid() and subcategory_form.is_valid():
            category = category_form.save()
            subcategory = subcategory_form.save(commit=False)
            subcategory.category = category
            subcategory.save()

            messages.success(request, "Category and Subcategory added successfully!")
            return redirect('home')

    else:
        category_form = CategoryForm()
        subcategory_form = SubCategoryForm()

    return render(request, 'add_category.html', {
        'category_form': category_form,
        'subcategory_form': subcategory_form
    })


def category_list(request):
    categories = Category.objects.prefetch_related('subcategories').all()
    return render(request, 'categories.html', {'categories': categories})

def get_top_selling_products():
    top_selling = (
        Product.objects.annotate(total_sold=Sum("cartitem__quantity"))
        .order_by("-total_sold")[:5]
    )

    if len(top_selling) < 3:
        top_selling = Product.objects.order_by("?")[:3]

    return top_selling


VALID_DISCOUNT_CODES = {123456: 10, 654321: 20}  
def checkout(request):
    total_price = Decimal("100.00")  

    if request.method == "POST":
        discount_code = request.POST.get("discount_code", "").strip()

        if discount_code.isdigit():
            discount_code = int(discount_code)
            if discount_code in VALID_DISCOUNT_CODES:
                discount_percentage = VALID_DISCOUNT_CODES[discount_code]
                discount_amount = (total_price * Decimal(discount_percentage)) / 100
                total_price -= discount_amount

    return render(request, "checkout.html", {"total_price": total_price})