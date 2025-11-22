from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import PurchaseRequest

User = get_user_model()
PURCHASE_REQUEST_URL = reverse('purchase-request-list-create')

class PurchaseRequestTestCase(APITestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user(
            email='staff@test.com',
            password='StrongPassword123',
            username='staffuser',
            role='staff'
        )

        # Create a normal user
        self.normal_user = User.objects.create_user(
            email='user@test.com',
            password='StrongPassword123',
            username='normaluser',
            role='user'
        )

        # Sample purchase request data
        self.purchase_data = {
            "title": "New Laptop",
            "description": "Purchase a new laptop for dev team",
            "amount": 2500,
            "proforma": "https://example.com/proforma.pdf"
        }

    def test_staff_can_create_purchase_request(self):
        """Staff user can create a purchase request"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(PURCHASE_REQUEST_URL, self.purchase_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        response_json = response.json()
        pr = PurchaseRequest.objects.get(id=response_json.get('id'))
  
        assert pr.created_by == self.staff_user
        assert response_json.get('title') == self.purchase_data['title']
        assert response_json.get('amount') == self.purchase_data['amount']
        assert response_json.get('proforma') == self.purchase_data['proforma']


    def test_non_staff_cannot_create_purchase_request(self):
        """Non-staff user should not be able to create a purchase request"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(PURCHASE_REQUEST_URL, self.purchase_data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
