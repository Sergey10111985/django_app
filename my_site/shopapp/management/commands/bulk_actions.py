from django.contrib.auth.models import User
from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Bulk actions started")

        result = Product.objects.filter(name__contains="Smartphone",).update(discount=22)

        print(result)
        # info = [
        #     ('Smartpone 1', 199, User.objects.get(pk=2)),
        #     ('Smartpone 2', 299, User.objects.get(pk=2)),
        #     ('Smartpone 3', 399, User.objects.get(pk=2)),
        # ]
        # products = [
        #     Product(name=name, price=price, created_by=user)
        #     for name, price, user in info
        # ]
        #
        # result = Product.objects.bulk_create(products)
        #
        # for obj in result:
        #     print(obj)


        self.stdout.write(f'Done!')
