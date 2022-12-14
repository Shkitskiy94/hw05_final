from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(template_name='users/logged_out.html'),
         name='logout'),
    path('login/', LoginView.as_view(template_name='users/login.html'),
         name='login'),
    path('password_reset/', views.ResetForm.
         as_view(), name='password_reset_form'),
    path('password_reset/done/', views.ResetDone.
         as_view(), name='password_reset_done'),
    path('password_change/', views.ChangeForm.
         as_view(), name='password_change_form'),
    path('password_change/done/', views.ChangeDone.
         as_view(), name='password_change_done'),
    path('reset/<uidb64>/<token>/', views.ResetConfirm.
         as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', views.ResetComplete.
         as_view(), name='password_reset_complete'),
]
