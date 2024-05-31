from django.contrib.sitemaps import Sitemap

from .models import Product

class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Product.objects.filter(archived=False).order_by('-pk')

    def lastmod(self, obj: Product):
        return obj.created_at
