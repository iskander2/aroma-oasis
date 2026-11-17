

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product,Order, OrderItem
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from .forms import ProfileForm
from django.db import transaction
from django.http import JsonResponse


def home(request):
    search_query = request.GET.get("search", "").strip()

    products = Product.objects.all().order_by("name", "volume_ml")

    if search_query:
        products = products.filter(name__icontains=search_query)

    cart = request.session.get("cart", {})

    for product in products:
        in_cart = cart.get(str(product.id), 0)
        product.available_quantity = product.quantity - in_cart

    return render(request, "shop/home.html", {
        "products": products,
        "search_query": search_query
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    variants = list(
        Product.objects.filter(
            name=product.name
        ).order_by("volume_ml")
    )

    # Ищем описание и характеристики среди всех объёмов
    fields = [
        "description",
        "top_notes",
        "heart_notes",
        "base_notes",
        "longevity",
        "sillage",
    ]

    for field in fields:
        if not getattr(product, field):
            for variant in variants:
                value = getattr(variant, field)
                if value:
                    setattr(product, field, value)
                    break

    cart = request.session.get("cart", {})

    for variant in variants:
        in_cart = cart.get(str(variant.id), 0)
        variant.available_quantity = variant.quantity - in_cart

    product.available_quantity = (
        product.quantity - cart.get(str(product.id), 0)
    )

    return render(request, "shop/product_detail.html", {
        "product": product,
        "variants": variants,
    })

def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        if product.quantity > 0:
            product.quantity -= 1
            product.save()

    return redirect("home")

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        if cart[product_id] < product.quantity:
            cart[product_id] += 1
        else:
            message = "Больше товара нет на складе!"
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "message": message})
            messages.error(request, message)
    else:
        if product.quantity > 0:
            cart[product_id] = 1
        else:
            message = "Товара нет на складе!"
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "message": message})
            messages.error(request, message)

    request.session["cart"] = cart

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True})

    return redirect(request.META.get("HTTP_REFERER", "/"))


@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})

    cart.pop(str(product_id), None)

    request.session["cart"] = cart

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True})

    return redirect("cart_detail")

def cart_detail(request):
    cart = request.session.get("cart", {})
    cart_products = []
    total = 0

    for product_id, quantity in list(cart.items()):
        product = Product.objects.filter(id=product_id).first()

        # Если товара больше нет в базе — убираем его из корзины
        if product is None:
            cart.pop(product_id, None)
            continue

        cart_products.append({
            "product": product,
            "quantity": quantity
        })

        total += product.price * quantity

    request.session["cart"] = cart

    return render(request, "shop/cart.html", {
        "cart_products": cart_products,
        "total": total
    })

@require_POST
def checkout(request):
    if not request.user.is_authenticated:
        return redirect("login")

    cart = request.session.get("cart", {})

    if not cart:
        messages.error(request, "Корзина пуста!")
        return redirect("cart_detail")

    customer_name = request.POST.get("customer_name", "").strip()
    phone = request.POST.get("phone", "").strip()
    address = request.POST.get("address", "").strip()

    if not customer_name or not phone or not address:
        messages.error(request, "Заполните все поля!")
        return redirect("cart_detail")

    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        if product.quantity < quantity:
            messages.error(request, "Недостаточно товара на складе!")
            return redirect("cart_detail")

        total += product.price * quantity
    with transaction.atomic():

        order = Order.objects.create(
            user=request.user,
            total_price=total,
            customer_name=customer_name,
            phone=phone,
            address=address
    )

        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                price=product.price,
                volume_ml=product.volume_ml,
                quantity=quantity
        )

            product.quantity -= quantity
            product.save()

    request.session["cart"] = {}

    return redirect("order_detail", order_id=order.id)
@require_POST
def increase_quantity(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)

    if product_id in cart:
        product = get_object_or_404(Product, id=product_id)

        if cart[product_id] < product.quantity:
            cart[product_id] += 1
        else:
            messages.error(request, "Больше товара нет на складе!")

    request.session["cart"] = cart

    return redirect("cart_detail")

@require_POST
def decrease_quantity(request, product_id):
    cart = request.session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    request.session["cart"] = cart

    return redirect("cart_detail")

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, "shop/order_detail.html", {
        "order": order
    })

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, "shop/register.html", {
        "form": form
    })

@require_POST
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'shop/my_orders.html', {
        'orders': orders
    })

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    orders_count = Order.objects.filter(user=request.user).count()

    total_spent = sum(
        order.total_price
        for order in Order.objects.filter(user=request.user)
    )

    return render(request, 'shop/profile.html', {
        'orders_count': orders_count,
        'total_spent': total_spent,
        'form': form
    })