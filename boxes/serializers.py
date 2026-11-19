from rest_framework import serializers

from .models import Box, Order, OrderItem, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product", "product_name", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_weight = serializers.FloatField(read_only=True)
    recommended_box = BoxSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "customer_name", "created_at", "items", "total_weight",
                  "packing_status", "recommended_box", "reason", "packing_plan"]
        read_only_fields = ["packing_status", "reason", "packing_plan"]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("An order needs at least one item.")
        return items

    def create(self, validated_data):
        items = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        OrderItem.objects.bulk_create([OrderItem(order=order, **i) for i in items])
        return order
