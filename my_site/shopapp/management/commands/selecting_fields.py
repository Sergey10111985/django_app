from django.contrib.auth.models import User
from django.core.management import BaseCommand
from shopapp.models import  Product


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Select fields")
        users = User.objects.values_list('username', flat=True)
        for user in users:
            print(user)

        products = Product.objects.values('pk', 'name')
        for product in products:
            print(product)
        self.stdout.write(f'Done!')
