
from django.contrib import admin
from .models import Product, Order, OrderItem



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "volume_ml",
        "quantity",
        "image",
    )

    search_fields = ("name",)

    list_filter = ("category", "volume_ml")

admin.site.register(OrderItem)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "total_price", "status")
    list_filter = ("status",)
