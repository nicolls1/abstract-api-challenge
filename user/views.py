from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models import Subscription, UserSubscription
from user.serializers import UserSerializer, CreateUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny],
            serializer_class=CreateUserSerializer)
    def signup(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        new_user = authenticate(username=serializer.validated_data['username'],
                                password=serializer.validated_data['password'])
        login(request, new_user)

        default_subscription_ids = Subscription.objects.filter(is_new_user_default=True)
        UserSubscription.objects.bulk_create([
            UserSubscription(user=new_user, subscription_id=subscription.id,
                             active_plan_id=subscription.get_free_tier_id())
            for subscription in default_subscription_ids
        ])

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
