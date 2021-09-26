from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from api.models import Api, Subscription, SubscriptionPlan


class ApiTestCase(TestCase):
    fixtures = ['basicdata.json']

    def test_admin_create(self):
        self.client.login(username='admin', password='admin')
        new_name = 'New'
        url = reverse('api-list')
        data = {
            'name': new_name,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], new_name)

    def test_admin_list(self):
        self.client.login(username='admin', password='admin')
        url = reverse('api-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_admin_retrieve(self):
        self.client.login(username='admin', password='admin')
        url = reverse('api-detail', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_create_error(self):
        self.client.login(username='user', password='user')
        new_name = 'New'
        url = reverse('api-list')
        data = {
            'name': new_name,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_list(self):
        self.client.login(username='user', password='user')
        url = reverse('api-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_user_retrieve(self):
        self.client.login(username='user', password='user')
        url = reverse('api-detail', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_user_api_subscription_plans(self):
        # Gender API
        self.client.login(username='user', password='user')
        url = reverse('api-subscription-plans', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertListEqual([plan['id'] for plan in response.data], [6, 7, 8])

        # Weather API
        self.client.login(username='user', password='user')
        url = reverse('api-subscription-plans', args=[2])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertListEqual([plan['id'] for plan in response.data], [14, 15])

    def test_signup_with_different_default_plan(self):
        weather_api = Api.objects.filter(name='Weather').get()
        first_subscription = Subscription.objects.filter(api=weather_api).order_by('id')[0]
        first_subscription.is_new_user_default = True
        first_subscription.save()
        first_subscription_plans = SubscriptionPlan.objects.filter(subscription=first_subscription) \
            .values_list('id', flat=True)

        url = reverse('user-signup')
        data = {
            'email': 'new@new.com',
            'username': 'new',
            'password': 'new',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # New Weather API Default
        url = reverse('api-subscription-plans', args=[weather_api.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertListEqual([plan['id'] for plan in response.data], list(first_subscription_plans))
