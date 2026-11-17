from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('buy/<int:product_id>/', views.buy_product, name='buy_product'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path(
    "cart/remove/<int:product_id>/",
    views.remove_from_cart,
    name="remove_from_cart"
),path("checkout/", views.checkout, name="checkout"),
path(
    'cart/increase/<int:product_id>/',
    views.increase_quantity,
    name='increase_quantity'
),path(
    'cart/decrease/<int:product_id>/',
    views.decrease_quantity,
    name='decrease_quantity'
),path(
    "order/<int:order_id>/",
    views.order_detail,
    name="order_detail"
),path("register/", views.register, name="register"),path('logout/', views.logout_view, name='logout'),
path(
    'login/',
    auth_views.LoginView.as_view(template_name='shop/login.html'),
    name='login'
),path('my-orders/', views.my_orders, name='my_orders'),path('profile/', views.profile, name='profile'),
]
