from django.db import models
from django.conf import settings


class Product(models.Model):

    VOLUME_CHOICES = [
        (5, "5 мл"),
        (10, "10 мл"),
        (20, "20 мл"),
        (50, "50 мл — целый флакон"),
        (100, "100 мл — целый флакон"),
    ]

    CATEGORY_CHOICES = [
        ("men", "Мужские"),
        ("women", "Женские"),
        ("unisex", "Унисекс"),
        ("unknown", "Не указано"),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    volume_ml = models.PositiveSmallIntegerField(
        choices=VOLUME_CHOICES,
        default=5
    )

    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default="unknown",
        verbose_name="Категория"
    )

    # Информация об аромате
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Описание аромата"
    )

    top_notes = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Верхние ноты"
    )

    heart_notes = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Ноты сердца"
    )

    base_notes = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Базовые ноты"
    )

    longevity = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Стойкость"
    )

    sillage = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Шлейф"
    )

    def __str__(self):
        return f"{self.name} — {self.volume_ml} мл"

class Order(models.Model):
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="orders"
)

    STATUS_CHOICES = [
        ("new", "Новый"),
        ("confirmed", "Подтверждён"),
        ("paid", "Оплачен"),
        ("shipped", "Отправлен"),
        ("completed", "Выполнен"),
        ("cancelled", "Отменён"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    customer_name = models.CharField(max_length=100, default="")
    phone = models.CharField(max_length=20, default="")
    address = models.TextField(default="")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new"
    )

    def __str__(self):
        return f"Заказ №{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )
    product_name = models.CharField(max_length=100)
    volume_ml = models.PositiveSmallIntegerField(default=5)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.product_name