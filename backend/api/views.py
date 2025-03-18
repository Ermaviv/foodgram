from django.db import IntegrityError
from djoser.views import UserViewSet as DjoserViewSet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from api.models import Ingredient, Recipe, Tag, User, Subscribe
from api.serializers import (
    TagSerializer,
    RecipeSerializer,
    IngredientSerializer,
    UserSerializer,
    SubscriptionsSerializer,
)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Recipe.objects.all()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserViewSet(DjoserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny,]

    def get_permissions(self):
        if self.action == "me" and self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated,]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['PUT', 'DELETE'],
        permission_classes=[IsAuthenticated,],
        url_path='me/avatar'
    )
    def set_delete_avatar(self, request):
        user = get_object_or_404(User, pk=self.request.user.pk)
        self.request.data['username'] = user.username
        if self.request.method == 'PUT':
            serializer = self.serializer_class(user, data=self.request.data)
            if serializer.is_valid():
                user.avatar = serializer.validated_data['avatar']
                user.save()
                serializer.save()
                return Response({'avatar': serializer.data['avatar']})
            return Response(serializer.errors)

        if self.request.method == 'DELETE':
            user.avatar = None
            serializer = self.serializer_class(user, data=self.request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(serializer.errors)

    @action(
        detail=False,
        methods=['GET',],
        permission_classes=[IsAuthenticated, ],
        url_path='subscriptions'
    )
    def get_list_subscription(self, request):
        if self.request.method == 'GET':
            user = get_object_or_404(User, pk=self.request.user.pk)
            self.request.data['username'] = user.username
            queryset = user.subscriptions.all()
            self.request.data['results'] = queryset
            serializer = self.serializer_class(user, data=self.request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'results': serializer.validated_data['is_subscribed']}, status=status.HTTP_200_OK)
            return Response(serializer.errors)

    @action(
        detail=False,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated, ],
        url_path='(?P<sub_id>\d+)/subscribe'
    )
    def add_delete_subscription(self, request, **kwargs):
        user = get_object_or_404(User, pk=self.request.user.pk)
        self.request.data['username'] = user.username
        user_subscribe = get_object_or_404(User, pk=self.kwargs['sub_id'])
        if self.request.method == 'POST':
            try:
                subscription = Subscribe.objects.create(user=user, subscription=user_subscribe)
            except IntegrityError:
                return Response(
                    {
                        'message':
                            'Ошибка подписки: или вы уже подписаны, или пытаетесь подписаться на себя.'
                     },
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.serializer_class(user, data=self.request.data)
            if serializer.is_valid():
                subscription.save()
                serializer.save()
                return Response({'results': serializer.validated_data['is_subscribed']}, status=status.HTTP_200_OK)
            return Response(serializer.errors)

        if self.request.method == 'DELETE':
            subscription = get_object_or_404(User, pk=self.kwargs['sub_id'])
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
