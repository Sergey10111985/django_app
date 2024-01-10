from django import forms
from django.core import validators

from shopapp.models import Product, Order


# class ProductForm(forms.Form):
#     name = forms.CharField(max_length=100)
#     price = forms.DecimalField(min_value=1, max_value=100000, decimal_places=2)
#     description = forms.CharField(
#         label='Product description',
#         widget=forms.Textarea(attrs={'rows': 5, 'cols': 30}),
#         validators=[validators.RegexValidator(
#             regex=r'great',
#             message='Some error description'
#         )],
#     )

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = 'name', 'price', 'description', 'discount'


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = 'delivery_address', 'products', 'promo_code', 'user'