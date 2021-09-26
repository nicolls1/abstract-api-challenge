from rest_framework import serializers

from api.models import Api, Subscription, SubscriptionPlan, UserSubscription


class ApiSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Api
        fields = ['url', 'id', 'create_time', 'name']
        read_only_fields = ['create_time']


class SubscriptionPlanSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['url', 'id', 'subscription', 'name', 'calls_allowed', 'unlimited_calls', 'price']


class PublicSubscriptionPlanSerializer(SubscriptionPlanSerializer):
    active = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = ['url', 'id', 'name', 'calls_allowed', 'unlimited_calls', 'price', 'active']

    def __init__(self, *args, active_plan_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_plan_id = active_plan_id

    def get_active(self, obj):
        return obj.id == self.active_plan_id


class CreateSubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subscription
        fields = ['url', 'id', 'create_time', 'api', 'is_new_user_default']
        read_only_fields = ['create_time']


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    plans = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['url', 'id', 'create_time', 'api', 'is_new_user_default', 'plans']
        read_only_fields = ['create_time', 'api']

    def get_plans(self, obj):
        queryset = SubscriptionPlan.objects.filter(subscription=obj.id).order_by('price')
        return SubscriptionPlanSerializer(queryset, many=True, context=self.context).data


class UserSubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ['url', 'id', 'user', 'subscription', 'active_plan']

    def validate(self, data):
        if data['active_plan'].subscription_id != data['subscription'].id:
            raise serializers.ValidationError('active_plan is not in subscription')
        return data

