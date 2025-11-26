from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from accounts.serializers import LoginSerializer, UserSerializer
from accounts.services import AuthService
from accounts.models import BlacklistedToken
from datetime import datetime, timezone

class LoginView(generics.GenericAPIView):
  permission_classes = [AllowAny]
  serializer_class = LoginSerializer
  def post(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.user
    
    jwt_access_token = AuthService.issue_access_token(user);
    response = {
      "status": "success",
      "message": "Login Successful",
      "data": {
        "access_token": str(jwt_access_token),
        "user":{
            'user_id': user.id,
            'username': user.username,
            'fullname': user.full_name,
            'email': user.email,
            'role': user.role,
        } 
      }
    }
    
    return Response(response, status=status.HTTP_200_OK)
  

class MeView(generics.GenericAPIView):
  """Return information about the currently authenticated user."""
  permission_classes = [IsAuthenticated]
  serializer_class = UserSerializer

  def get(self, request, *args, **kwargs):
    user = request.user
    serializer = self.get_serializer(user)
    response = {
      "status": "success",
      "data": {
        "user": serializer.data
      }
    }
    return Response(response, status=status.HTTP_200_OK)
  

class LogoutView(APIView):
  """Blacklist the currently used access token so it cannot be used again.

  Expects an `Authorization: Bearer <token>` header. The endpoint is protected
  with `IsAuthenticated` so a valid token is required to call it.
  """
  permission_classes = [IsAuthenticated]

  def post(self, request, *args, **kwargs):
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
      return Response({"status":"error","message":"Authorization header missing"}, status=status.HTTP_400_BAD_REQUEST)

    raw_token = auth.split()[1]
    try:
      token = AccessToken(raw_token)
    except Exception:
      return Response({"status":"error","message":"Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

    jti = token.get('jti')
    exp = token.get('exp')
    if not jti or not exp:
      return Response({"status":"error","message":"Token missing required claims"}, status=status.HTTP_400_BAD_REQUEST)

    expires = datetime.fromtimestamp(exp, tz=timezone.utc)

    # Create blacklist entry (idempotent)
    BlacklistedToken.objects.get_or_create(jti=jti, defaults={
      'token': raw_token,
      'expires_at': expires,
    })

    return Response({"status":"success","message":"Logged out. Bye!"}, status=status.HTTP_200_OK)
  