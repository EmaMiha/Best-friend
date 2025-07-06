from django.contrib import admin

# Register your models here.
<<<<<<< HEAD
from .models import Category, SubCategory, Cart
=======
from .models import Category, SubCategory
>>>>>>> ffd282190605125713a0abd263964f8a0e8f48d9

from django.contrib import admin
from .models import Order, OrderItem

<<<<<<< HEAD

=======
>>>>>>> ffd282190605125713a0abd263964f8a0e8f48d9
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

<<<<<<< HEAD

=======
>>>>>>> ffd282190605125713a0abd263964f8a0e8f48d9
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

<<<<<<< HEAD

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Cart)
=======
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
>>>>>>> ffd282190605125713a0abd263964f8a0e8f48d9


admin.site.register(Category)
admin.site.register(SubCategory)