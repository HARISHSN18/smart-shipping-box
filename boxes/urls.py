from django.urls import path

from . import views as v

urlpatterns = [
    path("", v.home, name="home"),
    path("products/", v.ProductList.as_view(), name="product_list"),
    path("products/add/", v.ProductCreate.as_view(), name="product_add"),
    path("products/<int:pk>/edit/", v.ProductUpdate.as_view(), name="product_edit"),
    path("products/<int:pk>/delete/", v.ProductDelete.as_view(), name="product_delete"),
    path("boxes/", v.BoxList.as_view(), name="box_list"),
    path("boxes/add/", v.BoxCreate.as_view(), name="box_add"),
    path("boxes/<int:pk>/edit/", v.BoxUpdate.as_view(), name="box_edit"),
    path("boxes/<int:pk>/delete/", v.BoxDelete.as_view(), name="box_delete"),
    path("orders/", v.order_list, name="order_list"),
    path("orders/new/", v.order_create, name="order_create"),
    path("orders/<int:pk>/", v.order_detail, name="order_detail"),
    path("orders/<int:pk>/recommend/", v.order_recommend, name="order_recommend"),
]
