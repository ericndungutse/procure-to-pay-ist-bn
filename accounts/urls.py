from django.urls import path
from .views import LoginView, MeView, LogoutView

urlpatterns = [
  path('login', LoginView.as_view(), name="api_auth_login"),
  path('me', MeView.as_view(), name="api_auth_me"),
  path('logout', LogoutView.as_view(), name="api_auth_logout"),
]