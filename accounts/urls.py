from django.urls import path
from .views import AccoutDetailsView, LoginView

urlpatterns = [
  path('login', LoginView.as_view(), name="api_auth_login"),
  path('me', AccoutDetailsView.as_view(), name="api_get_me"),
]