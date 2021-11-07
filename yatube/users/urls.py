from django.contrib.auth import views as v
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        v.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),
    path(
        'login/',
        v.LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change/',
        v.PasswordChangeView.as_view(
            template_name='users/password_change_form.html'),
        name='pass_change'
    ),
    path(
        'password_change/done/',
        v.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'),
        name='pass_change_done'
    ),
    path(
        'password_reset/',
        v.PasswordResetView.as_view(
            template_name='users/password_reset.html'),
        name='pass_reset'
    ),
    path(
        'password_reset/done/',
        v.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'),
        name='pass_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        v.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'),
        name='pass_reset_confirm'
    ),
    path(
        'reset/done/',
        v.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'),
        name='pass_reset_complete'
    ),
]
