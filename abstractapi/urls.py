"""abstractapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from user import views as user_views
from api import views as api_views

from rest_framework import urls

router = routers.DefaultRouter()
router.register(r'users', user_views.UserViewSet, basename='user')
router.register(r'apis', api_views.ApiViewSet, basename='api')
router.register(r'subscriptions', api_views.SubscriptionViewSet, basename='subscription')
router.register(r'subscription_plans', api_views.SubscriptionPlanViewSet, basename='subscriptionplan')
router.register(r'user_subscriptions', api_views.UserSubscriptionViewSet, basename='usersubscription')


urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls'))
]
