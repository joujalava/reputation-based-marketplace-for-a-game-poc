from accounts.models import Profile
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeDoneView, PasswordChangeView
from django.urls.base import reverse_lazy
from accounts.forms import ProfileUpdateForm, RegistrationForm, UserUpdateForm
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name='profile_detail.html'

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)

class RegistrationView(CreateView):
    template_name = 'registration.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:login')

class CustomLogOutView(LogoutView):
    template_name = 'auth/logged_out.html'

class CustomLogInView(LoginView):
    template_name = 'auth/login.html'

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'auth/password_change.html'
    success_url = reverse_lazy('accounts:password-change-done')

class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'auth/password_change_done.html'

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

class HomePageView(TemplateView):
    template_name = 'home.html'