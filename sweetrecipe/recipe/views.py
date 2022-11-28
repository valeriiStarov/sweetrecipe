from datetime import datetime

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, PasswordResetConfirmView,
                                       PasswordResetView)
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.forms import modelformset_factory
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, View)

from .forms import *
from .models import *
from .utils import *


class Home(DataMixin, ListView):
    """Главная страница"""
    model = Dessert
    template_name = 'recipe/home.html'
    context_object_name = 'desserts'
    paginate_by = 2

    def get_queryset(self):
        return Dessert.objects.get_queryset().order_by('id').select_related('profile')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Главная")
        return dict(list(context.items()) + list(c_def.items()))

class About(DataMixin, TemplateView):
    """Страница о нас"""
    template_name = 'recipe/about.html'
     
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="О нас")
        return dict(list(context.items()) + list(c_def.items()))


class AddRecipe(LoginRequiredMixin ,DataMixin, View):
    """Страница добавления рецепта"""
    template_name = 'recipe/addrecipe.html'
    login_url = 'login'
    # Здесь используются формсеты для динамического добавления формы, с текстом и фото рецепта
    AddRecipeFormSet = modelformset_factory(Recipe, form=AddRecipeForm, max_num=20, extra=1)

    def get(self, request, *args, **kwargs):
        self.object = self.get_user_context()
        formset = self.AddRecipeFormSet(queryset=Recipe.objects.none())

        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'title': 'Добавление рецепта',
                'main_form': AddRecipeMainForm(),
                'formset': formset,
            }
        )
 
    def post(self, request):
        main_form = AddRecipeMainForm(request.POST, request.FILES)
        formset = self.AddRecipeFormSet(request.POST, request.FILES)
        
        if main_form.is_valid() and formset.is_valid():
            main_form_comf = main_form.save(commit=False)
            
            for form in formset.save(commit=False):
                form.dessert = main_form_comf

            main_form_comf.profile = request.user.profile
            main_form.save()
            formset.save()
            

            return redirect(reverse_lazy('home'))
 
        return render(
            request,
            template_name=self.template_name,
            context={
                'main_form': main_form,
                'formset': formset,
                'menu_left': menu_left,
                'title': 'Добавление рецепта',
            }
        )


class ShowRecipe(DataMixin, View):
    """Страница с десертом и его рецептом"""
    template_name = 'recipe/recipe.html'
    slug_url_kwarg = 'recipe_slug'

    def get(self, request, *args, **kwargs):
        self.object = self.get_user_context()
        try:
            dessert = Dessert.objects.select_related('profile').get(slug = self.kwargs['recipe_slug'])
        except ObjectDoesNotExist:
            raise Http404
        comments = Comment.objects.filter(dessert = dessert).select_related('profile')
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right,
                'title': 'Рецепт' + ' ' + dessert.title,
                'dessert': dessert,
                'comments': comments,
                'form': CommentForm,
            }
        )
 
    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        dessert = Dessert.objects.select_related('profile').get(slug = self.kwargs['recipe_slug'])
        comments = Comment.objects.filter(dessert = dessert).select_related('profile')

        if form.is_valid():
            form_comf = form.save(commit=False)
            form_comf.profile = request.user.profile
            form_comf.dessert = dessert
            form_comf.save()

            return HttpResponseRedirect(self.request.path_info)
 
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right,
                'title': 'Рецепт' + ' ' + dessert.title,
                'dessert': dessert,
                'comments': comments,
                'form': form
            }
        )


class EditRecipe(LoginRequiredMixin, DataMixin, View):
    """Страница изменения десерта"""
    template_name = 'recipe/addrecipe.html'
    login_url = 'login'
    slug_url_kwarg = 'recipe_slug'
    AddRecipeFormSet = modelformset_factory(Recipe, form=AddRecipeForm, max_num=20, extra=1)

    def get(self, request, *args, **kwargs):
        self.object = self.get_user_context()
        formset = self.AddRecipeFormSet(queryset=Recipe.objects.filter(dessert__slug = self.kwargs['recipe_slug']))
        try:
            dessert = Dessert.objects.get(slug = self.kwargs['recipe_slug'])
        except ObjectDoesNotExist:
            raise Http404

        if dessert.profile.user == request.user:
            return render(
                request,
                template_name=self.template_name,
                context={
                    'menu_left': menu_left,
                    'title': 'Редактирование рецепта',
                    'main_form': AddRecipeMainForm(instance=dessert),
                    'formset': formset,
                    'dessert_url': dessert.slug
                }
            )
        else:
            raise PermissionDenied
    
    def post(self, request, *args, **kwargs):
        dessert = Dessert.objects.get(slug = self.kwargs['recipe_slug'])
        main_form = AddRecipeMainForm(request.POST, request.FILES, instance=dessert)
        formset = self.AddRecipeFormSet(request.POST, request.FILES)

        if main_form.is_valid() and formset.is_valid():
            
            main_form_comf = main_form.save(commit=False)
            
            for form in formset.save(commit=False):
                form.dessert = main_form_comf

            main_form_comf.user = request.user
            formset.save()
            main_form_comf.save()
            
            return redirect(reverse_lazy('home'))
 
        return render(
            request,
            template_name=self.template_name,
            context={
                'main_form': main_form,
                'formset': formset,
                'menu_left': menu_left,
                'title': 'Редактирование рецепта',
                'dessert_url': dessert.slug
            }
        )


class DeleteRecipe(LoginRequiredMixin, DataMixin, DetailView, DeleteView):
    """Страница удаления десерта"""
    model = Dessert
    template_name = 'recipe/recipe.html'
    login_url = 'login'
    slug_url_kwarg = 'recipe_slug'
    context_object_name = 'dessert'
    success_url = reverse_lazy('confirm_delete_recipe')

    def get_context_data(self, *args, **kwargs):
        dessert = Dessert.objects.get(slug = self.kwargs['recipe_slug'])
        if dessert.profile.user != self.request.user:
            raise PermissionDenied
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Удаление рецепта', delete_recipe=1)
        return dict(list(context.items()) + list(c_def.items()))

    
class ConfirmDeleteRecipe(LoginRequiredMixin, DataMixin, TemplateView):
    template_name = 'recipe/confirm_delete_recipe.html'
    login_url = 'login'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Рецепт удален')
        return dict(list(context.items()) + list(c_def.items()))


class CategoryList(DataMixin, ListView):
    """Страница со списком категорий"""
    model = Category
    template_name = 'recipe/category_list.html'
    context_object_name = 'categorys'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Категории")
        return dict(list(context.items()) + list(c_def.items()))

    
class ShowCategory(DataMixin, ListView):
    """Главная страница с десертами только выбранной категории"""
    paginate_by = 12
    template_name = 'recipe/home.html'
    model = Dessert
    context_object_name = 'desserts'
    slug_url_kwarg = 'category_slug'

    def get_queryset(self):
        return Dessert.objects.filter(category__slug=self.kwargs['category_slug']).prefetch_related('category')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(slug=self.kwargs['category_slug'])
        c_def = self.get_user_context(title="Категория - " +  str(category.name), category_name = category.name)

        return dict(list(context.items()) + list(c_def.items()))


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'recipe/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Регистрация")
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'recipe/login.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизация")
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')

    
def logout_user(request):
    logout(request)
    return redirect('home')


def pageNotFound(request, exception):
    return render(
        request,
        'recipe/404.html',
        status=404,
    )

def Forbidden(request, exception):
    return render(
        request,
        'recipe/403.html',
        status=403,
    )


class UserProfile(LoginRequiredMixin, DataMixin, DetailView):
    """Главная страница пользователя"""
    template_name = 'recipe/user_profile.html'
    login_url = 'login'

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title = 'Аккаунт',)
        return dict(list(context.items()) + list(c_def.items()))


class UserPersonalInfo(LoginRequiredMixin, DataMixin, DetailView):
    """Персональная информация пользователя"""
    template_name = 'recipe/user_personal_info.html'
    login_url = 'login'

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title = 'Личная информация',)
        return dict(list(context.items()) + list(c_def.items()))


class UserSecurity(LoginRequiredMixin, DataMixin, DetailView):
    """Страница безопасности пользователя"""
    template_name = 'recipe/user_security.html'
    login_url = 'login'

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title = 'Безопасность',)
        return dict(list(context.items()) + list(c_def.items()))


class UpdateUserPhoto(LoginRequiredMixin, DataMixin, View):
    """Обновления фото пользователя"""
    template_name = 'recipe/update_user.html'
    login_url = 'login'

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        self.object = self.get_user_context()

        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение фото профиля',
                'form': UpdateUserPhotoForm(),
            }
        )
    
    def post(self, request):
        form = UpdateUserPhotoForm(request.POST, request.FILES, instance=request.user.profile)
       

        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect(reverse_lazy('user_personal_info'))
 
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение фото профиля',
                'form': form
            }
        )


class UpdateUserName(LoginRequiredMixin, DataMixin, View):
    """Обновление имени пользователя"""
    template_name = 'recipe/update_user.html'
    login_url = 'login'

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    def get(self, request, *args, **kwargs):
       
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение имени профиля',
                'form': UpdateUserNameForm(),
            }
        )
    
    def post(self, request):
        form = UpdateUserNameForm(request.POST, instance=request.user.profile)
       
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect(reverse_lazy('user_personal_info'))
 
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение имени профиля',
                'form': form
            }
        )


class UpdateUserDateOfBirth(LoginRequiredMixin, DataMixin, View):
    """Обновление даты рождения пользователя"""
    template_name = 'recipe/update_user.html'
    login_url = 'login'

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    def get(self, request, *args, **kwargs):
       
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение даты рождения профиля',
                'form': UpdateUserDateOfBirthForm(),
            }
        )
    
    def post(self, request):
        form = UpdateUserDateOfBirthForm(request.POST, instance=request.user.profile)
       
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect(reverse_lazy('user_personal_info'))
 
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение даты рождения профиля',
                'form': form
            }
        )


class UpdateUserSex(LoginRequiredMixin, DataMixin, View):
    """Обновление пола пользователя"""
    template_name = 'recipe/update_user.html'
    login_url = 'login'

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    def get(self, request, *args, **kwargs):
       
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение пола профиля',
                'form': UpdateUserSexForm(),
            }
        )
    
    def post(self, request):
        form = UpdateUserSexForm(request.POST, instance=request.user.profile)
       
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect(reverse_lazy('user_personal_info'))
 
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение пола профиля',
                'form': form
            }
        )


class UpdateUserPhone(LoginRequiredMixin, DataMixin, View):
    """Обновление телефона пользователя"""
    template_name = 'recipe/update_user.html'
    login_url = 'login'

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    def get(self, request, *args, **kwargs):
       
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение телефона профиля',
                'form': UpdateUserPhoneForm(),
            }
        )
    
    def post(self, request):
        form = UpdateUserPhoneForm(request.POST, instance=request.user.profile)
       
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect(reverse_lazy('user_personal_info'))
 
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение телефона профиля',
                'form': form
            }
        )


class AuthUserPass(LoginRequiredMixin, DataMixin, View):
    """Страница подтверждения текущего пароля для смены пароля через личный кабинет"""
    template_name = 'recipe/auth_user_pass.html'
    login_url = 'login'

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    def get(self, request, *args, **kwargs):
       
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение пароля',
                'form': AuthUserPassForm(),
            }
        )
    
    def post(self, request):
        form = AuthUserPassForm(request.POST, instance=request.user)
       
        if form.is_valid():
            return redirect(reverse_lazy('update_user_pass'))
            
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение пароля',
                'form': form
            }
        )


class UpdateUserPass(LoginRequiredMixin,DataMixin, View):
    """Страница смены пароля через личный кабинет"""
    login_url = 'login'
    template_name = 'recipe/update_user_pass.html'
    
    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    def get(self, request, *args, **kwargs):
       
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение пароля',
                'form': UpdateUserPassForm(),
            }
        )
    
    def post(self, request):
        form = UpdateUserPassForm(request.POST)
       
        if form.is_valid():
            if form.cleaned_data['new_password1'] == form.cleaned_data['new_password2']:
                user = self.get_object()
                user.set_password(form.cleaned_data['new_password1'])
                user.profile.date_change_pass = datetime.now()
                user.save()
                login(self.request, user)
                return redirect(reverse_lazy('user_security'))
            
        return render(
            request,
            template_name=self.template_name,
            context={
                'menu_left': menu_left,
                'menu_right': menu_right[2:],
                'title': 'Изменение пароля',
                'form': form
            }
        )


class ShowUserDessert(DataMixin, ListView):
    """Главная страница с десертами только выбранного пользователя"""
    paginate_by = 12
    template_name = 'recipe/home.html'
    model = Dessert
    context_object_name = 'desserts'
    
    def get_queryset(self):
        return Dessert.objects.filter(profile__slug=self.kwargs['username_slug']).select_related('profile')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(slug=self.kwargs['username_slug'])
        c_def = self.get_user_context(title="Рецепты от " + str(profile.user.username), username_dessert = profile)
        return dict(list(context.items()) + list(c_def.items()))


# Смена пароля через почту 
# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

class PasswordResetView(DataMixin, PasswordResetView):
    template_name = 'recipe/reset_password.html'
    form_class = PasswordResetViewForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title = 'Смена пароля',)
        return dict(list(context.items()) + list(c_def.items()))


class PasswordResetConfirmView(DataMixin, PasswordResetConfirmView):
    template_name = 'recipe/password_reset_confirm.html'
    form_class = PasswordResetConfirmViewForm
    post_reset_login = True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title = 'Смена пароля',)
        return dict(list(context.items()) + list(c_def.items()))


class PasswordResetDoneView(DataMixin, TemplateView):
    template_name = 'recipe/password_reset_done.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title = 'Смена пароля',)
        return dict(list(context.items()) + list(c_def.items()))


class PasswordResetCompleteView(DataMixin, TemplateView):
    template_name = 'recipe/password_reset_complete.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title = 'Смена пароля',)
        return dict(list(context.items()) + list(c_def.items()))

# ^^^^^^^^^^^^^^^^^^^^^^^^
# Смена пароля через почту 


class AddCategory(DataMixin, CreateView):
    """Страница для администрации для добавления категории"""
    form_class = AddCategoryForm
    template_name = 'recipe/add_category.html'
    success_url = reverse_lazy('category_list')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_staff:
            raise PermissionDenied
        c_def = self.get_user_context(title="Добавление категории")
        return dict(list(context.items()) + list(c_def.items()))