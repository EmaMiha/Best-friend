from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('cart/', views.cart_view, name='cart_view'),
    path('logout/', views.logout_view, name='logout'),
    path('add-product/', views.add_product, name='add_product'),
    path(
        'add-to-cart/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart'),
    path('add-category/', views.add_category, name='add_category'),
    path('add-subcategory/', views.add_subcategory, name='add_subcategory'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.success_view, name='success'),
    path('cancel/', views.cancel_view, name='cancel'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path(
        'cart/remove/<int:item_id>/',
        views.remove_from_cart,
        name='remove_from_cart'),
    path(
        'get-subcategories/',
        views.get_subcategories,
        name='get_subcategories'),
    path("stripe-webhook/", views.stripe_webhook, name="stripe_webhook"),
    path('delete-product/<int:product_id>/',
         views.delete_product, name='delete_product'),
    path('update-product/<int:product_id>/',
         views.update_product, name='update_product'),
    path(
        'manage-categories/',
        views.manage_categories,
        name='manage_categories'),
    path('delete-category/<int:category_id>/',
         views.delete_category, name='delete_category'),
    path('delete-subcategory/<int:subcategory_id>/',
         views.delete_subcategory, name='delete_subcategory'),
    path('update-category/<int:category_id>/',
         views.update_category, name='update_category'),
    path('update-subcategory/<int:subcategory_id>/',
         views.update_subcategory, name='update_subcategory'),
    path('about/', views.about, name='about'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('subscribe/', views.newsletter_signup, name='newsletter_signup'),
    path('newsletter-subscribers/', views.view_subscribers, name='view_subscribers'),



]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
