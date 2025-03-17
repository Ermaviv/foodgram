from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        blank=True,
        unique=True
    )
    avatar = models.ImageField(
        'Выберите фото',
        blank=True,
        default=None
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]


class Tag(models.Model):
    tag = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='Название тега',
    )
    slug = models.SlugField(
        max_length=128,
        unique=True,
        verbose_name='Идентификатор тега',
        help_text='Идентификатор страницы для URL; разрешены символы латиницы,'
                  ' цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    title = models.CharField(
        max_length=64,
        verbose_name='Название ингредиента',
    )
    unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения',
    )

    def _str_(self):
        return self.title

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    tags = models.ForeignKey(
        Tag,
        verbose_name='Тэг',
        on_delete=models.CASCADE,
        null=True,
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='ингредиенты',
        related_name='ingredients',
    )
    favourites = models.ForeignKey(
        User,
        verbose_name='Кто добавил в избранное',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='favourites',
    )
    shopping_cart = models.ForeignKey(
        User,
        verbose_name='В чьих корзинах лежит',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cart',
    )
    name = models.CharField(
        max_length=128,
        verbose_name='Название рецепта',
        unique=True,
    )
    image = models.ImageField(
        'Выберите фото',
        upload_to='img',
    )
    text = models.TextField(
        max_length=256,
        verbose_name='Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='users')
    subscription = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions')

    class Meta:
        verbose_name = 'подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_prevent_self_follow",
                check=~models.Q(user=models.F("subscription")),
            ),
            models.UniqueConstraint(
                fields=['user', 'subscription'],
                name='unique_draft_user'
            )
        ]
