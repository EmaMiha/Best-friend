from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import ProductForm, CategoryForm
from .forms import SubCategoryForm, RegisterForm
from .models import (
    Product,
    Category,
    Cart,
    CartItem,
    Order,
    OrderItem,
    NewsletterSubscriber
)
from .models import SubCategory
from django.core.paginator import Paginator
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from itertools import zip_longest
from django.contrib.auth import logout
from .forms import NewsletterForm
from django.contrib.admin.views.decorators import staff_member_required


def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    top_selling_products = get_top_selling_products()
    top_products_grouped = group_products(top_selling_products, 3)

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
        "top_selling_products": top_selling_products,
        "top_products_grouped": top_products_grouped,
    })


def get_top_selling_products():
    top_selling = (
        Product.objects.annotate(total_sold=Sum("cartitem__quantity"))
        .order_by("-total_sold")[:6]
    )

    if len(top_selling) < 3:
        top_selling = Product.objects.order_by("?")[:3]

    return top_selling


def group_products(products, n):
    args = [iter(products)] * n
    return list(zip_longest(*args))


def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Successfully logged in!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]

            if User.objects.filter(username=username).exists():
                messages.error(
                    request,
                    "This username is already taken."
                    "Please choose another one."
                )
                return render(request, "register.html", {"form": form})

            if User.objects.filter(email=email).exists():
                messages.error(
                    request,
                    "This email is already in use."
                    "Please use a different email."
                )
                return render(request, "register.html", {"form": form})

            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            messages.success(
                request, "Registration successful! You can now log in.")
            return redirect("login")

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "User not authenticated"}, status=401)

    try:
        product = Product.objects.get(id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        data = json.loads(request.body.decode("utf-8"))
        quantity = int(data.get("quantity", 1))

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product)

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        cart_item.save()

        cart_count = CartItem.objects.filter(cart=cart).count()

        return JsonResponse(
            {"message": "Added to cart", "cart_count": cart_count})

    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


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

    return render(request, "cart.html", {
                  "cart_items": cart_items, "total_price": total_price})


@login_required
def create_checkout_session(request):
    print(">>> METHOD:", request.method)
    print(">>> POST DATA:", request.POST)

    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()

    if not cart_items:
        messages.error(request, "Your cart is empty!")
        return redirect("home")

    total_price = sum(
        item.product.price * item.quantity for item in cart_items
    )

    discount_code = request.POST.get(
        "discount_code_hidden", ""
    ).strip().upper()

    discount_percentage = VALID_DISCOUNT_CODES.get(discount_code, 0)
    discount_amount = (Decimal(discount_percentage) / 100) * total_price
    final_price = total_price - discount_amount

    line_items = []
    for item in cart_items:
        product_price = item.product.price
        if discount_percentage:
            product_price = (
                product_price * (
                    Decimal("100") - Decimal(discount_percentage)
                ) / 100
            )

        line_items.append({
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": item.product.name
                },
                "unit_amount": int((
                    product_price * 100
                ).quantize(Decimal("1"))),
            },
            "quantity": item.quantity,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/success/'),
        cancel_url=request.build_absolute_uri('/cancel/'),
    )

    order = Order.objects.create(
        user=request.user,
        total_price=final_price,
        stripe_payment_id=session.id
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order, product=item.product, quantity=item.quantity
        )

    cart_items.delete()

    return redirect(session.url)


def success_view(request):
    messages.success(
        request, "Payment successful! Your order has been placed.")
    return render(request, 'success.html')


def cancel_view(request):
    messages.error(request, "Payment was canceled. Please try again.")
    return render(request, 'cancel.html')


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def add_product(request):
    categories = Category.objects.all()

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully")
            return redirect("home")

    else:
        form = ProductForm()
    return render(request, 'add_product.html', {
                  'form': form, "categories": categories})


@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            messages.success(request, "Category added successfully!")
            return redirect('add_category')
    else:
        category_form = CategoryForm()

    subcategory_form = SubCategoryForm()
    return render(request, 'add_category.html', {
        'category_form': category_form,
        'subcategory_form': subcategory_form
    })


@user_passes_test(is_admin)
def add_subcategory(request):
    if request.method == 'POST':
        subcategory_form = SubCategoryForm(request.POST)
        if subcategory_form.is_valid():
            subcategory_form.save()
            messages.success(request, "Subcategory added successfully!")
            return redirect('add_category')
    else:
        subcategory_form = SubCategoryForm()

    category_form = CategoryForm()
    return render(request, 'add_category.html', {
        'category_form': category_form,
        'subcategory_form': subcategory_form
    })


def category_list(request):
    categories = Category.objects.prefetch_related('subcategories').all()
    return render(request, 'categories.html', {'categories': categories})


VALID_DISCOUNT_CODES = {"SAVE10": 10, "SAVE20": 20}


def checkout(request):
    print(">>> METHOD:", request.method)
    print(">>> POST DATA:", request.POST)
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cartitem_set.all()

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect("home")

        total_price = sum(
            item.product.price * item.quantity for item in cart_items
        )
        discount_percentage = 0
        discount_amount = Decimal("0.00")

        if request.method == "POST":
            print("POST data:", request.POST)
            discount_code = request.POST.get(
                "discount_code_hidden", ""
            ).strip().upper()
            print("Received discount code:", discount_code)

            if discount_code in VALID_DISCOUNT_CODES:
                discount_percentage = VALID_DISCOUNT_CODES[discount_code]
                discount_amount = (
                    total_price * Decimal(discount_percentage)
                ) / 100
                messages.success(
                    request,
                    f"Discount applied: {discount_percentage}% off"
                )
            else:
                messages.error(request, "Invalid discount code.")

            final_price = total_price - discount_amount
            if final_price < Decimal("0.01"):
                final_price = Decimal("0.01")

            line_items = []
            for item in cart_items:
                original_price = Decimal(item.product.price)
                discounted_price = original_price
                if discount_percentage > 0:
                    discounted_price = (
                        original_price * (
                            Decimal("100") - Decimal(discount_percentage)
                        ) / 100
                    )

                line_items.append({
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": item.product.name
                        },
                        "unit_amount": int((
                            discounted_price * 100
                        ).quantize(Decimal('1'))),
                    },
                    "quantity": item.quantity
                })

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=request.build_absolute_uri("/payment-success/"),
                cancel_url=request.build_absolute_uri("/cart/"),
            )

            order = Order.objects.create(
                user=request.user,
                total_price=final_price,
                status="pending",
                stripe_payment_id=checkout_session.id,
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )

            cart_items.delete()

            return redirect(checkout_session.url, code=303)

    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect("home")

    return render(
        request,
        "checkout.html",
        {
            "total_price": total_price,
            "discount_percentage": discount_percentage,
            "discount_amount": discount_amount
        }
    )


def get_subcategories(request):
    category_id = request.GET.get("category_id")

    if category_id:
        subcategories = SubCategory.objects.filter(
            category_id=category_id).values("id", "name")
        return JsonResponse({"subcategories": list(subcategories)})

    return JsonResponse({"subcategories": []})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        stripe_payment_id = session["id"]

        try:
            order = Order.objects.get(stripe_payment_id=stripe_payment_id)
            order.status = "completed"
            order.save()
            print(f"✅ Order {order.id} marked as completed!")
        except Order.DoesNotExist:
            print(f"❌ Order not found for payment ID: {stripe_payment_id}")

    return JsonResponse({"status": "success"}, status=200)


def cart_count(request):
    if request.user.is_authenticated:
        cart_items_count = CartItem.objects.filter(
            cart__user=request.user).count()
    else:
        cart_items_count = 0
    return {'cart_items_count': cart_items_count}


@login_required
@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('home')


@login_required
@user_passes_test(is_admin)
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('home')
    else:
        form = ProductForm(instance=product)

    return render(request, 'update_product.html', {
                  "form": form, "product": product})


def manage_categories(request):
    category_form = CategoryForm()
    subcategory_form = SubCategoryForm()
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    return render(request, 'add_category.html', {
        'category_form': category_form,
        'subcategory_form': subcategory_form,
        'categories': categories,
        'subcategories': subcategories,
    })


def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect('manage_categories')


def delete_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    subcategory.delete()
    messages.success(request, "Subcategory deleted successfully!")
    return redirect('manage_categories')


def update_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect("manage_categories")
    else:
        form = CategoryForm(instance=category)

    return render(request, "update_category.html", {"form": form})


def update_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
    if request.method == "POST":
        form = SubCategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, "Subcategory updated successfully!")
            return redirect('manage_categories')
    else:
        form = SubCategoryForm(instance=subcategory)
    return render(request, 'update_subcategory.html', {'form': form})


def about(request):
    return render(request, 'about.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out!")
    return redirect("home")


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})


def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "You've successfully subscribed to our newsletter!"
            )
        else:
            messages.error(
                request,
                "This email is already subscribed."
            )
    return redirect('home')


@staff_member_required
def view_subscribers(request):
    subscribers = NewsletterSubscriber.objects.all().order_by(
        '-subscribed_at'
    )
    return render(
        request,
        'newsletter_subscribers.html',
        {'subscribers': subscribers},
    )
