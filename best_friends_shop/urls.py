from django.contrib import admin
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
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add-category/', views.add_category, name='add_category'), 
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success_view, name='success'),
    path('cancel/', views.cancel_view, name='cancel'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)