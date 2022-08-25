from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import (PasswordResetView,
                                       PasswordResetDoneView,
                                       PasswordChangeView,
                                       PasswordChangeDoneView,
                                       PasswordResetConfirmView,
                                       PasswordResetCompleteView)
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class ResetForm(PasswordResetView):
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_form.html'


class ResetDone(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class ChangeForm(PasswordChangeView):
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


class ChangeDone(PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'


class ResetConfirm(PasswordResetConfirmView):
    success_url = reverse_lazy('users:password_reset_complete')
    template_name = 'users/password_reset_confirm.html'


class ResetComplete(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
