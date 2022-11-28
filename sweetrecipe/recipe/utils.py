from django.db.models import Count

from .models import *



menu_left = [
    {'title': "Категории", 'url_name': 'category_list'},
    {'title': "О нас", 'url_name': 'about'},
]
menu_right = [
    {'title': "Войти", 'url_name': 'login'},
    {'title': "Регистрация", 'url_name': 'register'},
    
]



class DataMixin:

    def get_user_context(self, **kwargs):
        context = kwargs
        user_menu_left = menu_left.copy()
        context['menu_left'] = user_menu_left
        user_menu_right = menu_right.copy()
        context['menu_right'] = user_menu_right
        return context