from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import generics, status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.serializers import LoginSerializer
from accounts.services import AuthService

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
  
  
class AccoutDetailsView(generics.GenericAPIView):
  def get(self, request, *args, **kwargs):
    return Response({"me": "is me"}, status=status.HTTP_200_OK)
