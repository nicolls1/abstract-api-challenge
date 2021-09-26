from rest_framework import viewsets, mixins
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import Api, Subscription, SubscriptionPlan, UserSubscription
from api.permissions import IsAdminOrReadOnly
from api.serializers import ApiSerializer, SubscriptionSerializer, SubscriptionPlanSerializer, \
    UserSubscriptionSerializer, PublicSubscriptionPlanSerializer, CreateSubscriptionSerializer


class ApiViewSet(viewsets.ModelViewSet):
    queryset = Api.objects.all().order_by('-id')
    serializer_class = ApiSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def subscription_plans(self, request, pk=None):
        api = self.get_object()
        # User should always have a subscription but in case they don't, add them to the default
        try:
            user_subscription = UserSubscription.objects.get(user=request.user, subscription__api=api)
        except UserSubscription.DoesNotExist as e:
            default_subscription = Subscription.objects.get(api=api, is_new_user_default=True)
            user_subscription = UserSubscription.objects.create(user=request.user, subscription=default_subscription,
                                                                active_plan_id=default_subscription.get_free_tier_id())
        plans = user_subscription.subscription.subscriptionplan_set.all().order_by('price')
        serializer = PublicSubscriptionPlanSerializer(plans, active_plan_id=user_subscription.active_plan_id, many=True,
                                                      context=self.get_serializer_context())
        return Response(serializer.data)


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all().order_by('-id')
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateSubscriptionSerializer
        return self.serializer_class


class SubscriptionPlanViewSet(mixins.CreateModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.ListModelMixin,
                              GenericViewSet):
    queryset = SubscriptionPlan.objects.all().order_by('-id')
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAdminUser]


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = UserSubscription.objects.all().order_by('-id')
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAdminUser]
