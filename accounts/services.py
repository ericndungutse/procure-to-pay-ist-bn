from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthService:
    """
    Handles all core authentication business logic, including token issuance 
    and output data structuring.
    """
    @staticmethod
    def issue_access_token(user):
      # 1. Generate Access Token (using RefreshToken utility)
      refresh = RefreshToken.for_user(user)
      access_token = str(refresh.access_token)

      # 2. Return the raw data needed by the view
      return access_token