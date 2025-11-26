
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()
LOGIN_URL = reverse('api_auth_login')
ME_URL = reverse('api_auth_me')
LOGOUT_URL = reverse('api_auth_logout')


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

    def test_get_current_user_with_token(self):
        """Test that /me returns the authenticated user's information."""
        # Log in to obtain token
        response = self.client.post(
            LOGIN_URL,
            {'email': self.email, 'password': self.password},
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        access_token = response_json.get('data', {}).get('access_token')
        assert access_token is not None

        # Set Authorization header and call /me
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        me_response = self.client.get(ME_URL)
        assert me_response.status_code == status.HTTP_200_OK
        me_json = me_response.json()
        user_data = me_json.get('data', {}).get('user')
        assert user_data is not None
        assert user_data.get('email') == self.email
        assert user_data.get('username') == self.username

    def test_logout_blacklists_token_and_denies_access(self):
        """Login, logout (blacklist), then ensure token is rejected."""
        # Log in to obtain token
        response = self.client.post(
            LOGIN_URL,
            {'email': self.email, 'password': self.password},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        access_token = response.json().get('data', {}).get('access_token')
        assert access_token is not None

        # Call logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_resp = self.client.post(LOGOUT_URL)
        assert logout_resp.status_code == status.HTTP_200_OK
        logout_json = logout_resp.json()
        assert logout_json.get('status') == 'success'

        # Subsequent request with same token should be unauthorized
        me_resp = self.client.get(ME_URL)
        assert me_resp.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

        # Ensure BlacklistedToken entry exists
        from accounts.models import BlacklistedToken
        # The jti of the token is stored, so check at least one entry exists
        assert BlacklistedToken.objects.count() >= 1
