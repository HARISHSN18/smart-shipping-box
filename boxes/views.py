from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .forms import BoxForm, ItemFormSet, OrderForm, ProductForm
from .models import Box, Order, Product
from .serializers import BoxSerializer, OrderSerializer, ProductSerializer
from .services import recommend_for_order

# ---------------------------------------------------------------- REST API


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer


class OrderViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.select_related("recommended_box").prefetch_related("items__product")
    serializer_class = OrderSerializer

    @action(detail=True, methods=["post"])
    def recommend(self, request, pk=None):
        """POST /api/orders/<id>/recommend/ - (re)calculate the best box."""
        order = recommend_for_order(self.get_object())
        return Response(self.get_serializer(order).data)


# ---------------------------------------------------------------- Web pages


def home(request):
    return render(request, "boxes/home.html", {
        "n_products": Product.objects.count(), "n_boxes": Box.objects.count(), "n_orders": Order.objects.count(),
        "recent": Order.objects.select_related("recommended_box").prefetch_related("items__product")[:5],
    })


class SafeDeleteView(DeleteView):
    template_name = "boxes/confirm_delete.html"

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, "This item is used by existing orders, so it can't be deleted.")
            return redirect(self.success_url)
        messages.success(self.request, "Deleted.")
        return response


class FormPage(SuccessMessageMixin):
    template_name = "boxes/form.html"
    success_message = "Saved."


class ProductList(ListView):
    model = Product
    template_name = "boxes/product_list.html"


class ProductCreate(FormPage, CreateView):
    model, form_class = Product, ProductForm
    success_url = reverse_lazy("product_list")
    extra_context = {"title": "Add product", "back": "product_list"}


class ProductUpdate(FormPage, UpdateView):
    model, form_class = Product, ProductForm
    success_url = reverse_lazy("product_list")
    extra_context = {"title": "Edit product", "back": "product_list"}


class ProductDelete(SafeDeleteView):
    model = Product
    success_url = reverse_lazy("product_list")
    extra_context = {"back": "product_list"}


class BoxList(ListView):
    model = Box
    template_name = "boxes/box_list.html"


class BoxCreate(FormPage, CreateView):
    model, form_class = Box, BoxForm
    success_url = reverse_lazy("box_list")
    extra_context = {"title": "Add shipping box", "back": "box_list"}


class BoxUpdate(FormPage, UpdateView):
    model, form_class = Box, BoxForm
    success_url = reverse_lazy("box_list")
    extra_context = {"title": "Edit shipping box", "back": "box_list"}


class BoxDelete(SafeDeleteView):
    model = Box
    success_url = reverse_lazy("box_list")
    extra_context = {"back": "box_list"}


def order_list(request):
    orders = Order.objects.select_related("recommended_box").prefetch_related("items__product")
    return render(request, "boxes/order_list.html", {"orders": orders})


def order_create(request):
    form = OrderForm(request.POST or None)
    formset = ItemFormSet(request.POST or None, instance=Order())
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            order = form.save()
            formset.instance = order
            formset.save()
        recommend_for_order(order)
        return redirect("order_detail", pk=order.pk)
    return render(request, "boxes/order_form.html", {"form": form, "formset": formset})


def order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related("recommended_box").prefetch_related("items__product"), pk=pk)
    return render(request, "boxes/order_detail.html", {"order": order})


@require_POST
def order_recommend(request, pk):
    recommend_for_order(get_object_or_404(Order, pk=pk))
    messages.success(request, "Recommendation recalculated.")
    return redirect("order_detail", pk=pk)
