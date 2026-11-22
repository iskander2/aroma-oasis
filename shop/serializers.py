from .models import Product, Order,OrderItem
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product_name',
            'volume_ml',
            'price',
            'quantity',
        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = [
            'id',
            'created_at',
            'total_price',
            'customer_name',
            'status',
            'items'
        ]

class OrderCreateItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Такого товара не существует."
            )

        return value


class OrderCreateSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()
    items = OrderCreateItemSerializer(many=True)

    def validate(self, data):
        requested = {}

        for item in data['items']:
            product_id = item['product_id']
            quantity = item['quantity']

            requested[product_id] = requested.get(product_id, 0) + quantity

        for product_id, quantity in requested.items():
            product = Product.objects.get(id=product_id)

            if product.quantity < quantity:
                raise serializers.ValidationError(
                    f"Недостаточно товара: {product.name}"
                )

        return data
    