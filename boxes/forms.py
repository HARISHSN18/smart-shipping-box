from django import forms
from django.forms import inlineformset_factory

from .models import Box, Order, OrderItem, Product


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "form-control")


class ProductForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "length", "width", "height", "weight"]
        labels = {"length": "Length (cm)", "width": "Width (cm)", "height": "Height (cm)", "weight": "Weight (kg)"}


class BoxForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Box
        fields = ["name", "length", "width", "height", "max_weight", "cost"]
        labels = {"length": "Internal length (cm)", "width": "Internal width (cm)", "height": "Internal height (cm)",
                  "max_weight": "Max weight (kg)", "cost": "Cost"}


class OrderForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name"]
        labels = {"customer_name": "Customer name (optional)"}


ItemFormSet = inlineformset_factory(
    Order, OrderItem, fields=("product", "quantity"), extra=3, min_num=1, validate_min=True, can_delete=False,
    widgets={"product": forms.Select(attrs={"class": "form-select"}),
             "quantity": forms.NumberInput(attrs={"class": "form-control", "min": 1})},
)
