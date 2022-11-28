from xml.dom import ValidationErr
from django import template
from django.contrib.auth.models import User
from django.forms import ValidationError

from recipe.models import *


register = template.Library()


@register.simple_tag(name='order_by_name')
def get_order_categories():
    return Category.objects.order_by('name')
