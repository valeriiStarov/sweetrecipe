from django.contrib import admin
from django.utils.safestring import mark_safe 

from .models import *


class DessertAdmin(admin.ModelAdmin):
    list_display = ('title', 'time_create', 'get_html_photo', 'is_published')
    prepopulated_fields = {"slug": ("title", )}
    fields = ('title', 'slug', 'category', 'ingredients', 'description', 'cooking_time','profile', 'photo', 'get_html_photo', 'is_published', 'time_create', 'time_update')
    readonly_fields = ('time_create', 'time_update', 'get_html_photo')

    def get_html_photo(self, object):
        if object.photo:
            return mark_safe(f"<img src='{object.photo.url}' width = 50>")

    get_html_photo.short_description = "Фото"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {"slug": ("name", )}
    fields = ('name', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe_text', 'image', 'dessert')
    fields = ('recipe_text', 'image', 'dessert')
    

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name')
    fields = ('user', 'photo', 'name', 'date_of_birth', 'date_change_pass', 'sex', 'phone')

admin.site.register(Dessert, DessertAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Comment)