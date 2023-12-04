from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

def shop_index(request: HttpRequest):
    products = [
        ('laptop', 2000),
        ('desktop', 3000),
        ('smartphone', 1000),
        ('tv', 2500),
        ('music station', 499.99),
    ]
    context = {
        'products': products,
    }
    return render(request, 'shopapp/shop-index.html', context=context)
