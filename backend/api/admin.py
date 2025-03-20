from django.contrib import admin

from .models import Ingredient, Recipe, Tag, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_active'
    )
    list_editable = (
        'is_active',
    )
    search_fields = ('email', 'username')
    list_display_links = ('username',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_display_links = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'tags',
        'author',
        'favourites'
    )
    search_fields = ('author', 'title')
    list_filter = ('tags',)
    list_display_links = ('tags',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'tag',
        'slug'
    )
    search_fields = ('tag',)
    list_display_links = ('tag',)
