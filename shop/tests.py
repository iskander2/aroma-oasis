from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import Order,Product

User = get_user_model()

class AllOrdersAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username='test_admin',
            password='testpassword123',
            is_staff=True
        )

        self.token = Token.objects.create(user=self.admin)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )

    def test_admin_can_get_all_orders(self):
        response = self.client.get('/api/orders/')

        self.assertEqual(response.status_code, 200)

    def test_regular_user_cannot_get_all_orders(self):
        user = User.objects.create_user(
            username='test_customer',
            password='testpassword123',
            is_staff=False
        )

        token = Token.objects.create(user=user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.get('/api/orders/')

        self.assertEqual(response.status_code, 403)
    def test_guest_cannot_get_all_orders(self):
        self.client.credentials()

        response = self.client.get('/api/orders/')

        self.assertEqual(response.status_code, 403)
    def test_user_sees_only_own_orders(self):
        user1 = User.objects.create_user(
            username='customer1',
            password='testpassword123'
        )

        user2 = User.objects.create_user(
            username='customer2',
            password='testpassword123'
        )

        order1 = Order.objects.create(
            user=user1,
            total_price=1000,
            customer_name='Customer 1',
            phone='123456',
            address='Bishkek'
        )

        Order.objects.create(
            user=user2,
            total_price=2000,
            customer_name='Customer 2',
            phone='654321',
            address='Bishkek'
        )

        token = Token.objects.create(user=user1)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.get('/api/my-orders/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order1.id)

    def test_user_cannot_view_other_order(self):
        user1 = User.objects.create_user(username='customer1')
        user2 = User.objects.create_user(username='customer2')

        other_order = Order.objects.create(
            user=user2,
            total_price=2000,
            customer_name='Customer 2',
            phone='654321',
            address='Bishkek'
        )

        token = Token.objects.create(user=user1)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.get(
            f'/api/my-orders/{other_order.id}/'
        )

        self.assertEqual(response.status_code, 404)
    def test_user_can_create_order(self):
        user = User.objects.create_user(
            username='order_customer',
            password='testpassword123'
        )

        product = Product.objects.create(
            name='Test Perfume',
            price='500.00',
            quantity=5
        )

        token = Token.objects.create(user=user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        data = {
            'customer_name': 'Test Customer',
            'phone': '+996555123456',
            'address': 'Bishkek',
            'items': [
                {
                    'product_id': product.id,
                    'quantity': 2
                }
            ]
        }

        response = self.client.post(
            '/api/create-order/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        product.refresh_from_db()
        self.assertEqual(product.quantity, 3)

        order = Order.objects.get(user=user)
        self.assertEqual(order.total_price, 1000)
    def test_order_fails_if_not_enough_stock(self):
        user = User.objects.create_user(
            username='stock_customer',
            password='testpassword123'
        )

        product = Product.objects.create(
            name='Test Perfume',
            price='500.00',
            quantity=5
        )

        token = Token.objects.create(user=user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        data = {
            'customer_name': 'Test Customer',
            'phone': '+996555123456',
            'address': 'Bishkek',
            'items': [
                {
                    'product_id': product.id,
                    'quantity': 7
                }
            ]
        }

        response = self.client.post(
            '/api/create-order/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, 400)

        product.refresh_from_db()
        self.assertEqual(product.quantity, 5)

        self.assertFalse(Order.objects.filter(user=user).exists())
    def test_user_can_cancel_own_order(self):
        user = User.objects.create_user(
            username='cancel_customer',
            password='testpassword123'
        )

        product = Product.objects.create(
            name='Test Perfume',
            price='500.00',
            quantity=3
        )

        order = Order.objects.create(
            user=user,
            total_price=1000,
            customer_name='Test Customer',
            phone='+996555123456',
            address='Bishkek',
            status='new'
        )

        from .models import OrderItem

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            price=product.price,
            volume_ml=product.volume_ml,
            quantity=2
        )

        product.quantity -= 2
        product.save()

        token = Token.objects.create(user=user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.post(
            f'/api/cancel-order/{order.id}/',
            {},
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        order.refresh_from_db()
        product.refresh_from_db()

        self.assertEqual(order.status, 'cancelled')
        self.assertEqual(product.quantity, 3)
    def test_regular_user_cannot_change_order_status(self):
        user = User.objects.create_user(
            username='status_customer',
            password='testpassword123'
        )

        order = Order.objects.create(
            user=user,
            total_price=1000,
            customer_name='Test Customer',
            phone='+996555123456',
            address='Bishkek',
            status='new'
        )

        token = Token.objects.create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )

        response = self.client.patch(
            f'/api/orders/{order.id}/status/',
            {'status': 'confirmed'},
            format='json'
        )

        self.assertEqual(response.status_code, 403)

        order.refresh_from_db()
        self.assertEqual(order.status, 'new')
