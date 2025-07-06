from django.contrib import admin

# Register your models here.
from .models import Category, SubCategory, Cart, NewsletterSubscriber
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]
    
    
@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Cart)


admin.site.register(Category)
admin.site.register(SubCategory)