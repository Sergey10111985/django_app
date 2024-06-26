import os

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse




def poduct_preview_directory_path(instance: "Product", filename: str) -> str:
    return "products/product_{pk}/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


class Product(models.Model):
    """
    Модель Product представляет товар,
    который можно продавать в интернет-магазине.

    Заказы тут: :model:`shopapp.Order`
    """
    class Meta:
        ordering = ['name', 'price']
        # db_table = 'tech_products'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    name = models.CharField(max_length=100, verbose_name=_('name'), db_index=True)
    description = models.TextField(null=False, blank=True, verbose_name=_('description'), db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2, verbose_name=_('price'))
    discount = models.SmallIntegerField(default=0, verbose_name=_('discount'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    archived = models.BooleanField(default=False, verbose_name=_('archived'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('created by'), default=2)
    preview = models.ImageField(null=True, blank=True, upload_to=poduct_preview_directory_path, verbose_name=_('preview'))

    def __str__(self) -> str:
        return f'Product(pk={self.pk}, name = {self.name!r})'

    def get_absolute_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.pk})


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return 'products/product_{pk}/images/{filename}'.format(
        pk=instance.product.pk,
        filename=filename
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.TextField(max_length=200, null=False, blank=True)


class Order(models.Model):
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    delivery_address = models.TextField(null=False, blank=True, verbose_name=_('delivery address'))
    promo_code = models.CharField(max_length=20, null=False, blank=True, verbose_name=_('promo code'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders', verbose_name=_('user id'), default=2)
    products = models.ManyToManyField(Product, related_name='orders', verbose_name=_('products'))
    receipt = models.FileField(null=True, upload_to='orders/receipts/', verbose_name=_('receipt'))

