from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Order, Product


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)
    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def save_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding=encoding,
    )
    reader = DictReader(csv_file)
    for row in reader:
        order = Order.objects.create(
            delivery_address=row["delivery_address"],
            promo_code=row["promo_code"],
        )
        products_ids = row["products"].split(",")
        order.products.set(products_ids)

