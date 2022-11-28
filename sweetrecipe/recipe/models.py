from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import time


class Dessert(models.Model):
    """Создание модели десерта"""
    title = models.CharField(max_length=255, verbose_name="Название десерта")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    ingredients = models.TextField(verbose_name="Ингредиенты")
    description = models.TextField(verbose_name="Описание")
    photo = models.ImageField(upload_to="photos/%Y/%m/%d", verbose_name="Главное фото")
    cooking_time = models.PositiveSmallIntegerField(verbose_name="Время готовки (в минутах)")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(default=True, verbose_name="Публикация")
    category = models.ManyToManyField('Category', related_name="category")
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='profile', blank=True, default=None)
    

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        """URL основной страницы десерта"""
        return reverse('recipe', kwargs={'recipe_slug': self.slug})

    def get_edit_url(self):
        """URL редактирования десерта"""
        return reverse('edit_recipe', kwargs={'recipe_slug': self.slug})

    def get_delete_url(self):
        """URL удаления рецепта"""
        return reverse('delete_recipe', kwargs={'recipe_slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = title_to_slug(self.title)
        super().save(*args, **kwargs)

    def cooking_time_mod(self) -> str:
        """Обработчик окончания для минут"""
        minute = str(self.cooking_time)[-2:]

        if int(minute) % 10 == 1 and int(minute) != 11:
            minute = 'минута'
        elif int(minute) % 10 in [2, 3, 4]:
            minute = 'минуты'
        else:
            minute = 'минут'

        return str(self.cooking_time) + ' ' + minute



class Recipe(models.Model):
    """Создание пошагового рецепта для десерта"""
    recipe_text = models.TextField(verbose_name="Рецепт")
    image = models.ImageField(upload_to="photos/%Y/%m/%d", verbose_name="Фото")
    dessert = models.ForeignKey('Dessert', on_delete=models.CASCADE, related_name='recipe', blank=True)

    def __str__(self) -> str:
        return self.dessert.title
    

class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    class Meta:
        ordering = ['name']
    
    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse('showcategory', kwargs={'category_slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = title_to_slug(self)
        super().save(*args, **kwargs)

    

def title_to_slug(title: str) -> str:
    """Преобразует название десерта в slug"""
    slug = ""
    dic = {'ь':'', 'ъ':'', 'а':'a', 'б':'b','в':'v',
       'г':'g', 'д':'d', 'е':'e', 'ё':'yo','ж':'zh',
       'з':'z', 'и':'i', 'й':'y', 'к':'k', 'л':'l',
       'м':'m', 'н':'n', 'о':'o', 'п':'p', 'р':'r', 
       'с':'s', 'т':'t', 'у':'u', 'ф':'f', 'х':'h',
       'ц':'ts', 'ч':'ch', 'ш':'sh', 'щ':'sch', 'ы':'yi',
       'э':'e', 'ю':'yu', 'я':'ya'}

    for t in slugify(title, allow_unicode=True):
        if t in dic:
            slug += dic[t]
        else:
            slug += t

    slug += "-" + str(int(time.time()))
    return slug


CHOICE = [(1,'Женский'),(0, 'Мужской')]
class Profile(models.Model):
    """Профиль пользователя создающийся по сигналам при создании User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    photo = models.ImageField(upload_to="users_photos/%Y/%m/%d", verbose_name="Фото профиля", blank=True)
    photo_base = models.FilePathField(path="users_photos/userphoto.jpg", blank=True)
    name = models.CharField(verbose_name="Имя", max_length=50, blank=True)
    date_of_birth = models.DateField(verbose_name="Дата рождения", blank=True, null=True)
    date_change_pass = models.DateTimeField(verbose_name="Дата изменения пароля", blank=True, null=True)
    sex = models.BooleanField(verbose_name="Пол",choices=CHOICE, blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True, null=True)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")

    def __str__(self) -> str:
        return self.user.username

    def get_absolute_url(self):
        return reverse('show_user_dessert', kwargs={'username_slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = title_to_slug(self)
        super().save(*args, **kwargs)

    def name_or_username(self):
        if not self.name:
            name = self.user.username
        else:
            name = self.name
        return name


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """При создании User будет создаваться его пустой Profile"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """При сохрании User, Profile также сохраняется"""
    instance.profile.save()


class Comment(models.Model):
    text = models.TextField(verbose_name="Оставьте комментарий")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_comment', blank=True, default=None)
    dessert = models.ForeignKey('Dessert', on_delete=models.CASCADE, related_name='dessert_comment', blank=True, default=None) 

    def __str__(self) -> str:
        return self.user.username