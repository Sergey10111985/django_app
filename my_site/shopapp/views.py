"""
В этом модуле лежат различные наборы представлений.

Разные view  интернет-магазина: по товарам, заказам и т.д.
"""

import logging
from csv import DictWriter
from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.request import Request
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy

from .common import save_csv_products
from .forms import GroupForm, ProductForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer

# from my_site.settings import INTERNAL_IPS

logger = logging.getLogger(__name__)


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ['name', 'description']
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived"
    ]
    ordering_fields = [
        'pk',
        "name",
        "price",
        "discount",
    ]

    @extend_schema(
        summary="Get one product by id",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = 'products-export.csv'
        response['Content-Disposition'] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(methods=['post'], detail=False, parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"],
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)

        return Response(serializer.data)


class OrdersViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ['delivery_address']
    filterset_fields = [
        "delivery_address",
        "promo_code",
        "created_at",
        "user",
        "products",
    ]
    ordering_fields = [
        'pk',
        "created_at",
        "user",
    ]


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        links = [
            'orders/',
            'groups/',
            'products/',
        ]
        context = {
            'links': links,
            'items': 1,
        }
        logger.debug('List of links: %s', links)
        logger.info('Rendering shop index')
        # logger.critical('HERE IT IS', INTERNAL_IPS)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            'form': GroupForm(),
            'groups': Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailView(DetailView):
    template_name = 'shopapp/product-details.html'
    # model = Product
    queryset = Product.objects.prefetch_related('images')
    context_object_name = 'product'


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        return response

    model = Product
    fields = ['name', 'price', 'description', 'discount', 'preview']
    success_url = reverse_lazy('shopapp:products_list')


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        if self.request.user.is_superuser:
            return True

        self.object = self.get_object()

        has_edit_perm = self.request.user.has_perm("shopapp.change_product")
        created_by_current_user = self.object.created_by == self.request.user
        return has_edit_perm and created_by_current_user

    model = Product
    # fields = ['name', 'price', 'description', 'discount', 'preview']
    template_name_suffix = '_update_form'
    form_class = ProductForm

    def form_valid(self, form):
        files = form.cleaned_data["images"]
        for image in files:
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs={'pk': self.object.pk}
        )


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )


class OrderCreateView(CreateView):
    model = Order
    fields = ['delivery_address', 'products', 'promo_code', 'user']
    success_url = reverse_lazy('shopapp:orders_list')


class OrderUpdateView(UpdateView):
    model = Order
    fields = ['delivery_address', 'products', 'promo_code', 'user']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs={'pk': self.object.pk}
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('shopapp:orders_list')


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by('pk').all()
        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived,
            }
            for product in products
        ]
        elem = products_data[0]
        name = elem["name"]
        print("name:", name)
        return JsonResponse({"products": products_data})


class OrdersDataExportView(UserPassesTestMixin, View):

    def test_func(self):
        if self.request.user.is_staff:
            return True

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by('id').all()
        orders_data = [
            {
                "pk": order.id,
                "delivery_address": order.delivery_address,
                "promo_code": order.promo_code,
                "user_id": order.user_id,
                "products": [p.id for p in order.products.all()],
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})



class LatestProductsFeed(Feed):
    title = "Latest Article Feed"
    description = "Updates on changes and addition blog Articles"

    link = reverse_lazy('blogapp:article-list')

    def items(self):
        return Product.objects.filter(archived=False)

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:50]

