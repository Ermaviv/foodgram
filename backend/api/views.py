import io

from django.db import IntegrityError
from django.db.models import Count
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.models import Ingredient, Recipe, Subscribe, Tag, User
from api.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    UserSerializer
)
from renderers import CSVStudentDataRenderer

RECIPES_ON_PAGE = 6


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    paginate_by = RECIPES_ON_PAGE

    def get_queryset(self):
        return super().get_queryset().annotate(
            count=Count("name")
        )

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart'
    )
    def get_recipe_to_shop_cart(self, request, **kwargs):
        '''
        if request.user.is_anonymous:
            anonymous = get_object_or_404(User, user='anonymous')
            cart = ShopCart.object.update_or_create(user=anonymous)
        else:
            cart = ShopCart.object.update_or_create(user=self.request.user)
        '''
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        recipe.shopping_cart = get_object_or_404(User, pk=self.request.user.pk)
        recipe.save()
        return Response(status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
        renderer_classes=[CSVStudentDataRenderer]
    )
    def download_shopping_cart(self, request):
        content = []
        queryset = self.get_queryset().filter(shopping_cart=self.request.user)
        for recipe in queryset:
            for ingredient in recipe.ingredients:
                content.append(ingredient.name)
        content_as_text = ""
        for idx, ingredient_name in content:
            content_as_text += f"{idx}. {ingredient_name}\n"
        file = io.BytestIO(content_as_text.encode())
        file.seek(0)
        return FileResponse(file, filename="shopping_list.txt")
    '''
    def download(self, request):
        user = get_object_or_404(User, pk=self.request.user.pk)
        queryset = user.cart.all()
        serializer = self.serializer_class(data=queryset)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(serializer.data)
    '''


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserViewSet(DjoserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    paginate_by = RECIPES_ON_PAGE
    pagination_class = LimitOffsetPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        return super().get_queryset().annotate(
            count=Count("email")
        )

    def get_permissions(self):
        if self.action == "me" and self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['PUT', 'DELETE'],
        permission_classes=[IsAuthenticated],
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
        methods=['GET'],
        permission_classes=[IsAuthenticated],
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
                return Response(
                    {'results': serializer.validated_data['is_subscribed']},
                    status=status.HTTP_200_OK
                )
            return Response(serializer.errors)

    @action(
        detail=False,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated, ],
        url_path=r'(?P<sub_id>\d+)/subscribe'
    )
    def add_delete_subscription(self, request, **kwargs):
        user = get_object_or_404(User, pk=self.request.user.pk)
        self.request.data['username'] = user.username
        user_subscribe = get_object_or_404(User, pk=self.kwargs['sub_id'])
        if self.request.method == 'POST':
            try:
                subscription = Subscribe.objects.create(
                    user=user,
                    subscription=user_subscribe
                )
            except IntegrityError:
                return Response(
                    {
                        'message':
                            'Ошибка подписки: или вы уже подписаны,'
                            'или пытаетесь подписаться на себя.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.serializer_class(user, data=self.request.data)
            if serializer.is_valid():
                subscription.save()
                serializer.save()
                return Response(
                    {'results': serializer.validated_data['is_subscribed']},
                    status=status.HTTP_200_OK
                )
            return Response(serializer.errors)

        if self.request.method == 'DELETE':
            subscription = get_object_or_404(User, pk=self.kwargs['sub_id'])
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


'''
class IngredientViewSet(DjoserViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    search_fields = ('name',)
'''
