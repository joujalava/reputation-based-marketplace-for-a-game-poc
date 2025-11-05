from django.urls import path
from .views import CustomLogOutView, CustomLogInView, CustomPasswordChangeDoneView, CustomPasswordChangeView, ProfileDetailView, ProfileUpdateView, RegistrationView, UserUpdateView

app_name = 'accounts'
urlpatterns = [
    path('login/', CustomLogInView.as_view(), name='login'),
    path('logout/', CustomLogOutView.as_view(), name='logout'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password-change'),
    path('password_change/done', CustomPasswordChangeDoneView.as_view(), name='password-change-done'),
    path('account_update/', UserUpdateView.as_view(), name='user-update'),
    path('profile/', ProfileDetailView.as_view(), name='profile'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('change_character_name/', ProfileUpdateView.as_view(), name='character-name-change')
]
