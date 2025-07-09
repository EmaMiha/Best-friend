from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product


class ProductSitemap(Sitemap):
    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return f"/product/{obj.id}/"


class StaticViewSitemap(Sitemap):
    def items(self):
        return ['home', 'about', 'cart_view']

    def location(self, item):
        return reverse(item)
