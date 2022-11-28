from django.urls import path

from .views import *


urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('about/', About.as_view(), name='about'),
    path('addrecipe/', AddRecipe.as_view(), name='addrecipe'),
    path('recipe/<slug:recipe_slug>/', ShowRecipe.as_view(), name='recipe'),
    path('category-list/', CategoryList.as_view(), name='category_list'),
    path('category/<slug:category_slug>/', ShowCategory.as_view(), name='showcategory'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('user-profile/', UserProfile.as_view(), name='user_profile'),
    path('user-personal-info/', UserPersonalInfo.as_view(), name='user_personal_info'),
    path('user-security/', UserSecurity.as_view(), name='user_security'),
    path('update-user-photo/', UpdateUserPhoto.as_view(), name='update_user_photo'),
    path('update-user-name/', UpdateUserName.as_view(), name='update_user_name'),
    path('update-user-date-of-birth/', UpdateUserDateOfBirth.as_view(), name='update_user_date_of_birth'),
    path('update-user-sex/', UpdateUserSex.as_view(), name='update_user_sex'),
    path('update-user-phone/', UpdateUserPhone.as_view(), name='update_user_phone'),
    path('auth-user-pass/', AuthUserPass.as_view(), name='update_pass'),
    path('update-user-pass/', UpdateUserPass.as_view(), name='update_user_pass'),
    path('show_user_dessert/<str:username_slug>/', ShowUserDessert.as_view(), name='show_user_dessert'),
    path('edit-recipe/<slug:recipe_slug>/', EditRecipe.as_view(), name='edit_recipe'),
    path('delete-recipe/<slug:recipe_slug>/', DeleteRecipe.as_view(), name='delete_recipe'),
    path('confirm-delete-recipe/', ConfirmDeleteRecipe.as_view(), name='confirm_delete_recipe'),
    path('reset-password/', PasswordResetView.as_view(), name ='reset_password'),
    path('password-reset-done/', PasswordResetDoneView.as_view(), name ='password_reset_done'),
    path('reset/<uidb64>/<token>', PasswordResetConfirmView.as_view(template_name = "recipe/password_reset_confirm.html"), name ='password_reset_confirm'),
    path('reset_password_complete/', PasswordResetCompleteView.as_view(), name ='password_reset_complete'),
    path('add-category/', AddCategory.as_view(), name='add_category'),
]
