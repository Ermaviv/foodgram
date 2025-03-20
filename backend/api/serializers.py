import base64

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.files.base import ContentFile
from rest_framework import serializers
from api.models import Ingredient, Tag, Recipe, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            # Затем декодировать сами данные и поместить результат в файл,
            # которому дать название по шаблону.
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=128,
        validators=[UnicodeUsernameValidator()]
    )
    is_subscribed = serializers.BooleanField(
        allow_null=True,
        default=None,
        required=False,
    )
    avatar = Base64ImageField(
        required=False,
        allow_null=True
    )
    is_in_shopping_cart = serializers.BooleanField(
        default=False
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',
                  'is_in_shopping_cart', 'avatar'
                  )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True)
    author = UserSerializer(
        read_only=True,
    )
    count = serializers.IntegerField(
        default=0
    )

    class Meta:
        model = Recipe
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class SubscriptionsSerializer(serializers.ModelSerializer):
    results = UserSerializer()

    class Meta:
        model = User
        fields = '__all__'
