from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django_currentuser.middleware import get_current_authenticated_user
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


from .models import *


class AddRecipeMainForm(forms.ModelForm):
    """Форма для основной части десерта"""
    prepopulated_fields = {"slug": ("title", )}

    class Meta:
        model = Dessert
        fields = ['title', 'photo', 'ingredients', 'description', 'cooking_time', 'category', 'profile']

        widgets = {
            'title': forms.TextInput(attrs=
            {'class': 'form-control',
            'placeholder': 'Например: Торт "Молочная девочка"'}),
            'photo': forms.FileInput(attrs=
            {'class': 'form-control'}),
            'ingredients': forms.Textarea(attrs=
            {'class': 'form-control',
            'rows': 9,
            'placeholder': 'Например:\nсгущенное молоко - 300г\nяйцо - 3шт\nсоль - 1щепотка\nмука пшеничная - 180г\nразрыхлитель - 10г\nсливки 33% - 500г\nванильный сахар - 10г\nягоды свежие'}),
            'description': forms.Textarea(attrs=
            {'class': 'form-control',
            'placeholder': 'Например: Необычайно нежный и вкусный торт «Молочная девочка» приготовить очень быстро и просто. Этот рецепт не займет много вашего времени и усилий, зато результат порадует всех. Нежные, мягкие коржи на сгущенном молоке в сочетании с кремом из сливок и сгущенки, по вкусу напоминающим сливочное мороженое. Перед этим тортом устоять невозможно!'}),
            'cooking_time': forms.NumberInput(attrs=
            {'class': 'form-control',
            'placeholder': 'Например: 30'}),
            'category': forms.CheckboxSelectMultiple(attrs=
            {'type': 'checkbox'}),
            'profile': forms.HiddenInput,
        }
        labels = {
            'category': 'Категория',
            'profile': '',
        }
        help_texts = {
            'title': 'В названии можно использовать знаки: "-" "," и кавычки',
            'cooking_time': 'Максимум 240 минут'
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 60:
            raise ValidationError('Длина названия не должна превышать 60 символов')

        sign_list = """!()[]{};?@#$%:'\./^&;*_"""
        for t in title:
            if t in sign_list:
                raise ValidationError(f'Знак "{t}" нельзя использовать в названии')
        return title

    def clean_cooking_time(self):
        cooking_time = self.cleaned_data['cooking_time']
        if cooking_time > 240:
            raise ValidationError('Максимальное время готовки 240 минут')

        return cooking_time



class AddRecipeForm(forms.ModelForm):
    """Форма для пошагового рецепта для десерта"""
    class Meta:
        model = Recipe
        fields = ['recipe_text', 'image', 'dessert']

        widgets = {
            'recipe_text': forms.Textarea(attrs=
            {'class': 'form-control', 'rows': 7}),
            'image': forms.FileInput(attrs=
            {'class': 'form-control'}),
            'dessert': forms.HiddenInput
        }

        labels = {
            'dessert': ''
        }


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control',
    'placeholder':'email@email.com'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль должен содержать как минимум 8 символов'}))
    password2 = forms.CharField(label='Подтверждение нового пароля', widget=forms.PasswordInput(attrs=
    {'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise ValidationError("Данный email уже зарегистрирован")
        return email


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={'class': 'form-control'})
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        user = self.cleaned_data['username']
        try:
            User.objects.get(username=user)
        except User.DoesNotExist:
            raise ValidationError("Данный пользователь не зарегистрирован")
        return user

    def clean_password(self):
        try:
             self.cleaned_data['username']
        except KeyError:
            raise ValidationError("Неверное имя пользователя")

        password = self.cleaned_data['password']
        if User.objects.get(username=self.cleaned_data['username']).check_password(password):
            return password
        else:
            raise ValidationError("Неверный пароль")


class UpdateUserPhotoForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('photo',)

        widgets = {
            'photo': forms.FileInput(attrs=
            {'class': 'form-control'}),
        }


class UpdateUserNameForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('name',)

        widgets = {
            'name': forms.TextInput(attrs=
            {'class': 'form-control'})
        }


class UpdateUserDateOfBirthForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('date_of_birth',)

        widgets = {
            'date_of_birth': forms.DateInput(attrs=
            {'type': 'date'}),
        }

    def clean_date_of_birth(self):
        """Проверка введенного возраста на соответствие форме"""
        date_of_birth = self.cleaned_data['date_of_birth']
    
        if date_of_birth >= datetime.now().date():
            raise ValidationError("Дата рождения не может быть больше текущего времени")
        elif relativedelta(parse(str(datetime.now().date())), parse(str(date_of_birth))).years < 12:
            raise ValidationError("Вам должно быть не менее 12 лет")
        else:
            return date_of_birth


class UpdateUserSexForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ('sex',)

        widgets = {
            'sex': forms.RadioSelect()
        }

    def __init__(self, *args, **kwargs):
        super(UpdateUserSexForm, self).__init__(*args, **kwargs)
        if self.fields['sex'].widget.choices[0][0] == "" :
            del self.fields['sex'].widget.choices[0]


class UpdateUserPhoneForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('phone',)

        widgets = {
            'phone': forms.TextInput(attrs=
            {'class': 'form-control'})
        }

    def clean_phone(self):
        """Проверка введенного телефона на соответсвие форме"""
        phone = list(self.cleaned_data['phone'])
        if phone[0] == "+":
            phone.pop(0)
        for p in phone:
                if not p.isnumeric():
                    raise ValidationError('Неверный формат номера телефона')
        if len(phone) > 11:
            raise ValidationError('Указанный номер имеет более 11 цифр')
        elif len(phone) < 11:
            raise ValidationError('Указанный номер имеет менее 11 цифр')
        else:
            if not (phone[0] == '7' or phone[0] == '8'):
                raise ValidationError('Номер должен начинаться на 7 или 8')
            else:
                phone.pop(0)
        return ('8 ({}{}{}) {}{}{}-{}{}-{}{}'.format(*''.join(phone)))


class AuthUserPassForm(forms.ModelForm):
    """Форма подтверждения текущего пароля при запросе на смену пароля"""
    class Meta:
        model = User
        fields = ('password', )

        widgets = {
            'password': forms.PasswordInput(attrs=
            {'class': 'form-control',
            'placeholder':'Введите пароль'})
        }

    def clean_password(self):
        user = get_current_authenticated_user()
        password = self.cleaned_data['password']
        if user.check_password(password):
            return password
        else:
            raise ValidationError("Неверный пароль")
    


class UpdateUserPassForm(forms.Form):
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(
    attrs={'class': 'form-control'}), help_text="Пароль должен содержать не менее 8 символов")
    new_password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput(
    attrs={'class': 'form-control'}))

    def clean_new_password1(self):
        password = self.cleaned_data['new_password1']

        if len(password) < 8:
            raise ValidationError("Пароль должен содержать не менее 8 символов")
        else:
            return password


class PasswordResetViewForm(PasswordResetForm):
    email = forms.EmailField(label='Адрес электронной почты', widget=forms.EmailInput(attrs={'class': 'form-control',
    'placeholder':'Введите Email'}))

    class Meta:
        model = User
        fields = ('email', )


class PasswordResetConfirmViewForm(SetPasswordForm):
    new_password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль должен содержать как минимум 8 символов'}))
    new_password2 = forms.CharField(label='Подтверждение нового пароля', widget=forms.PasswordInput(attrs=
    {'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text', 'dessert')

        widgets = {
            'text': forms.Textarea(attrs=
            {'class': 'form-control', 'rows': 3}),
            'dessert': forms.HiddenInput
        }
        
        labels = {
            'dessert': ''
        }


class AddCategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ('name',)

        widgets = {
            'name': forms.TextInput(attrs=
            {'class': 'form-control'}),
        }