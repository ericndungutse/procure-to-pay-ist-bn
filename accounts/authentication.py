from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import BlacklistedToken


class CustomJWTAuthentication(JWTAuthentication):
    """Extends simplejwt's JWTAuthentication to reject blacklisted tokens.

    It checks the token's 'jti' claim against the `BlacklistedToken` table.
    """
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        jti = token.get('jti')
        if jti and BlacklistedToken.objects.filter(jti=jti).exists():
            raise AuthenticationFailed('Token has been blacklisted! Please login again to get access.')
        return token
