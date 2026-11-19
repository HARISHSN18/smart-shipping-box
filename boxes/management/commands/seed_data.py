from django.core.management.base import BaseCommand

from boxes.models import Box, Product


class Command(BaseCommand):
    help = "Load sample boxes and products"

    def handle(self, *args, **opts):
        for n, l, w, h, mw, c in [("XS", 20, 15, 10, 2, "0.40"), ("S", 30, 20, 15, 5, "0.70"),
                                  ("M", 40, 30, 20, 10, "1.10"), ("L", 55, 40, 30, 20, "1.80"),
                                  ("XL", 70, 50, 40, 30, "2.90")]:
            Box.objects.update_or_create(name=n, defaults=dict(length=l, width=w, height=h, max_weight=mw, cost=c))
        for n, l, w, h, wt in [("Phone case", 15, 8, 1.5, 0.05), ("T-shirt", 28, 20, 3, 0.2),
                               ("Ceramic mug", 10, 10, 11, 0.4), ("Running shoes", 32, 20, 12, 0.9),
                               ("Hardcover book", 24, 17, 4, 0.6), ("Laptop", 36, 25, 2.5, 2.0),
                               ("Blender", 20, 20, 40, 2.5)]:
            Product.objects.update_or_create(name=n, defaults=dict(length=l, width=w, height=h, weight=wt))
        self.stdout.write(self.style.SUCCESS("Sample boxes and products loaded."))
