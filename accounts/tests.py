
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()
LOGIN_URL = reverse('api_auth_login')


class LoginTestCase(APITestCase):

    def setUp(self):
        self.email = 'test@test.com'
        self.password = 'StrongPassword123'
        self.username = 'testuser'

        # Create user
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            username=self.username
        )

    def test_successful_login_and_token_issue(self):
        """Test login success returns access token"""
        response = self.client.post(
            LOGIN_URL,
            {'email': self.email, 'password': self.password},
            format='json'  # DRF automatically handles JSON
        )

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()

        assert response_json.get('status') == 'success'
        assert response_json.get('message') == 'Login Successful'

        access_token = response_json.get('data', {}).get('access_token')
        assert access_token is not None
        assert isinstance(access_token, str)
        assert len(access_token) > 10

    def test_login_failure_invalid_password(self):
        """Test login with wrong password fails"""
        response = self.client.post(
            LOGIN_URL,
            {'email': self.email, 'password': 'WrongPassword456'},
            format='json'
        )

        response_json = response.json()

        # Either your serializer returns 'non_field_errors' or a message key
        error_msg = response_json.get('non_field_errors')
        if error_msg:
            assert "Invalid credentials." in error_msg[0]
        else:
            # fallback if your view returns status/message
            assert response_json.get('status') == 'fail'
            assert "Invalid credentials" in response_json.get('message', "")
