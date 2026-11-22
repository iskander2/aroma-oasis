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
),path('my-orders/', views.my_orders, name='my_orders'),path('profile/', views.profile, name='profile'), path('api/products/', views.product_list, name='api_product_list'),
path('api/products/<int:product_id>/', views.api_product_detail, name='api_product_detail'),
path('api/my-orders/', views.my_orders_api, name='api_my_orders'),path('api/my-orders/<int:order_id>/', views.my_order_detail_api, name='api_my_order_detail'),path('api/create-order/', views.create_order_api, name='api_create_order'),path('api/cancel-order/<int:order_id>/', views.cancel_order_api, name='api_cancel_order'),path(
    'api/orders/<int:order_id>/status/',
    views.update_order_status_api,
    name='api_update_order_status'
),path('api/orders/', views.all_orders_api, name='api_all_orders'),
]
