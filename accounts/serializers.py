from rest_framework import serializers
from django.contrib.auth import authenticate 
from django.contrib.auth import get_user_model


User = get_user_model() 

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True, 
        style={'input_type': 'password'}
    )

    user = None 

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        request = self.context.get('request')

        if email and password:
            user_obj = authenticate(request=request, username=email,password=password)
            print(user_obj)

            if user_obj is None:
                raise serializers.ValidationError("Invalid credentials.")

            self.user = user_obj
            return data
          
        raise serializers.ValidationError("Must include email and password.")