from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from .forms import OrderForm, GroupForm, ProductForm
from .models import Product, Order, ProductImage


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
