from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Api(models.Model):
    create_time = models.DateTimeField('api create time', default=timezone.now)
    name = models.CharField('api name', max_length=255)

    def __str__(self):
        return f'{self.name}({self.id})'


class Subscription(models.Model):
    api = models.ForeignKey(Api, on_delete=models.CASCADE, verbose_name='api for subscription')
    create_time = models.DateTimeField('plan create time', default=timezone.now)
    is_new_user_default = models.BooleanField('is new users be assigned by default')

    def save(self, *args, **kwargs):
        # only allow one entry per api to be is_new_user_default
        if self.is_new_user_default:
            Subscription.objects.filter(api=self.api, is_new_user_default=True).update(is_new_user_default=False)
        return super().save(*args, **kwargs)

    def get_free_tier_id(self):
        try:
            return SubscriptionPlan.objects.get(subscription=self, price=0).id
        except SubscriptionPlan.DoesNotExist:
            return None

    def __str__(self):
        return f'{self.api.name} API at {self.create_time.strftime("%d.%m.%y %H:%M")} ({self.id})'


class SubscriptionPlan(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE,
                                     verbose_name='subscription plan belongs to')
    name = models.CharField('plan name', max_length=255)
    calls_allowed = models.IntegerField('calls per month allowed', default=0)
    unlimited_calls = models.BooleanField('ignore "calls_allowed" field as unlimited are allowed', default=False)
    price = models.FloatField('monthly price')

    def __str__(self):
        return f'{self.name}({self.id}) for subscription "{self.subscription}"'


class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE,
                                     verbose_name='subscription')

    class Meta:
        unique_together = ['user', 'subscription']

    active_plan = models.ForeignKey(SubscriptionPlan, blank=True, null=True, on_delete=models.CASCADE,
                                    verbose_name='active plan for user')
