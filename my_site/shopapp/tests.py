from datetime import datetime
from string import ascii_letters
from random import choices
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase

from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers
from django.urls import reverse


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(1, 2)
        self.assertEqual(result, 3)


class ProductCreateTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="testBob", password="qwerty")
        cls.user.user_permissions.add(Permission.objects.get(codename='add_product'))

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_product_create(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                'name': self.product_name,
                'price': "155.50",
                'description': "A table",
                'discount': "10"
            }
        )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="testBob", password="qwerty")
        cls.product = Product.objects.create(name="NEW product", created_by=cls.user)

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)
        print(self.product)

    def test_get_product(self):
        response = self.client.get(reverse("shopapp:product_details", kwargs={'pk': self.product.id}))
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(reverse("shopapp:product_details", kwargs={'pk': self.product.id}))
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
        'user-fixture.json',
        'auth-group-fixture.json',
    ]

    def test_product_list(self):
        response = self.client.get(reverse("shopapp:products_list"))
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context['products']),
            transform=lambda p: p.pk
        )
        self.assertTemplateUsed(response, "shopapp/products-list.html")


class OrdersListViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username="testBob", password="qwerty")
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'user-fixture.json',
        'auth-group-fixture.json',
        'products-fixture.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:products_export"))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        print(expected_data)
        print('*' * 100)
        print(products_data)
        self.assertEqual(products_data["products"], expected_data)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="testBob", password="qwerty")
        cls.user.user_permissions.add(Permission.objects.get(codename='view_order'))

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            delivery_address='Test Address',
            promo_code='Test Promocode',
            user=self.user,
        )

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(reverse("shopapp:order_details", kwargs={'pk': self.order.id}))
        self.assertContains(response, self.order.delivery_address)
        self.assertContains(response, self.order.promo_code)
        self.assertEqual(response.context["order"].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = [
        'user-fixture.json',
        'auth-group-fixture.json',
        'products-fixture.json',
        'orders-fixture.json',
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="TestBob", password="qwerty")
        cls.user.is_staff = True
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:orders_export"))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by('id').all()
        expected_data = [
            {
                "pk": order.id,
                "delivery_address": order.delivery_address,
                "promo_code": order.promo_code,
                "user_id": order.user_id,
                "products": [p.id for p in order.products.all()],
            }
            for order in orders
        ]
        products_data = response.json()
        self.assertEqual(products_data["orders"], expected_data)
