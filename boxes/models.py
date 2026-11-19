from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

POSITIVE = [MinValueValidator(0.01)]
POSITIVE_DECIMAL = [MinValueValidator(Decimal("0.01"))]


class Product(models.Model):
    name = models.CharField(max_length=200)
    length = models.FloatField(validators=POSITIVE, help_text="cm")
    width = models.FloatField(validators=POSITIVE, help_text="cm")
    height = models.FloatField(validators=POSITIVE, help_text="cm")
    weight = models.FloatField(validators=POSITIVE, help_text="kg")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Box(models.Model):
    """Shipping box. Dimensions are INTERNAL (usable) size in cm."""
    name = models.CharField(max_length=100, unique=True)
    length = models.FloatField(validators=POSITIVE)
    width = models.FloatField(validators=POSITIVE)
    height = models.FloatField(validators=POSITIVE)
    max_weight = models.FloatField(validators=POSITIVE, help_text="kg")
    cost = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE_DECIMAL)

    class Meta:
        ordering = ["cost"]
        verbose_name_plural = "boxes"

    @property
    def volume(self):
        return self.length * self.width * self.height

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Not packed yet"
        PACKED = "PACKED", "All items fit"
        NO_BOX = "NO_BOX", "No suitable box"

    customer_name = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    packing_status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    recommended_box = models.ForeignKey(Box, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    reason = models.TextField(blank=True)
    packing_plan = models.JSONField(null=True, blank=True)  # placements used by the 3D viewer

    class Meta:
        ordering = ["-id"]

    @property
    def total_weight(self):
        return round(sum(i.line_weight for i in self.items.all()), 3)

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    @property
    def line_weight(self):
        return self.product.weight * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product}"
