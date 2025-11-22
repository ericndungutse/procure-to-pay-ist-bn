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

    def test_staff_can_get_only_own_purchase_requests(self):
        """Staff user should only see their own purchase requests"""
        # Create another staff user
        other_staff_user = User.objects.create_user(
            email='otherstaff@test.com',
            password='StrongPassword123',
            username='otherstaffuser',
            full_name='Other Staff User',
            role='staff'
        )

        # Create purchase requests for both staff users
        pr1 = PurchaseRequest.objects.create(
            title="My Request",
            amount=1000,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING
        )
        
        pr2 = PurchaseRequest.objects.create(
            title="Other Staff Request",
            amount=2000,
            created_by=other_staff_user,
            status=PurchaseRequest.Status.PENDING
        )

        # Staff user should only see their own request
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(PURCHASE_REQUEST_URL)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        
        assert response_json['status'] == 'success'
        assert response_json['message'] == 'Purchase requests retrieved successfully'
        assert response_json['size'] == 1
        assert len(response_json['data']['purchase_requests']) == 1
        assert response_json['data']['size'] == 1
        
        # Check the purchase request data
        pr_data = response_json['data']['purchase_requests'][0]
        assert pr_data['id'] == str(pr1.id)
        assert pr_data['title'] == pr1.title
        assert pr_data['amount'] == pr1.amount
        assert pr_data['status'] == pr1.status
        assert pr_data['created_by_name'] == self.staff_user.full_name
        assert 'created_at' in pr_data

    def test_approver_can_get_all_purchase_requests(self):
        """Approver user should see all purchase requests"""
        # Create approver user
        approver = User.objects.create_user(
            email='approver@test.com',
            password='StrongPassword123',
            username='approveruser',
            full_name='Approver User',
            role='approver-level-1'
        )

        # Create another staff user
        other_staff_user = User.objects.create_user(
            email='staff2@test.com',
            password='StrongPassword123',
            username='staff2user',
            full_name='Staff User 2',
            role='staff'
        )

        # Create purchase requests for both users
        pr1 = PurchaseRequest.objects.create(
            title="Request 1",
            amount=1000,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING
        )
        
        pr2 = PurchaseRequest.objects.create(
            title="Request 2",
            amount=2000,
            created_by=other_staff_user,
            status=PurchaseRequest.Status.APPROVED
        )

        # Approver should see all requests
        self.client.force_authenticate(user=approver)
        response = self.client.get(PURCHASE_REQUEST_URL)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        
        assert response_json['status'] == 'success'
        assert response_json['size'] == 2
        assert len(response_json['data']['purchase_requests']) == 2
        
        # Verify both requests are present
        pr_ids = [pr['id'] for pr in response_json['data']['purchase_requests']]
        assert str(pr1.id) in pr_ids
        assert str(pr2.id) in pr_ids

    def test_finance_can_get_all_purchase_requests(self):
        """Finance user should see all purchase requests"""
        # Create finance user
        finance_user = User.objects.create_user(
            email='finance@test.com',
            password='StrongPassword123',
            username='financeuser',
            full_name='Finance User',
            role='finance'
        )

        # Create purchase requests from different users
        pr1 = PurchaseRequest.objects.create(
            title="Finance Request 1",
            amount=1500,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING
        )
        
        pr2 = PurchaseRequest.objects.create(
            title="Finance Request 2",
            amount=3000,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.REJECTED
        )

        # Finance user should see all requests
        self.client.force_authenticate(user=finance_user)
        response = self.client.get(PURCHASE_REQUEST_URL)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        
        assert response_json['status'] == 'success'
        assert response_json['size'] == 2
        assert len(response_json['data']['purchase_requests']) == 2

    def test_get_all_purchase_requests_response_structure(self):
        """Test that GET response contains all required fields"""
        # Update staff user with full_name for proper testing
        self.staff_user.full_name = 'Staff Test User'
        self.staff_user.save()

        # Create a purchase request
        pr = PurchaseRequest.objects.create(
            title="Test Request",
            amount=5000,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING
        )

        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(PURCHASE_REQUEST_URL)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        
        # Check response structure
        assert 'status' in response_json
        assert 'message' in response_json
        assert 'size' in response_json
        assert 'data' in response_json
        assert 'size' in response_json['data']
        assert 'purchase_requests' in response_json['data']
        
        # Check purchase request fields
        pr_data = response_json['data']['purchase_requests'][0]
        assert 'id' in pr_data
        assert 'title' in pr_data
        assert 'amount' in pr_data
        assert 'status' in pr_data
        assert 'created_at' in pr_data
        assert 'created_by_name' in pr_data
        
        # Verify field values
        assert pr_data['id'] == str(pr.id)
        assert pr_data['title'] == pr.title
        assert pr_data['amount'] == pr.amount
        assert pr_data['status'] == pr.status
        assert pr_data['created_by_name'] == self.staff_user.full_name

    def test_get_all_purchase_requests_empty_list(self):
        """Test GET request when there are no purchase requests"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(PURCHASE_REQUEST_URL)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        
        assert response_json['status'] == 'success'
        assert response_json['size'] == 0
        assert response_json['data']['size'] == 0
        assert len(response_json['data']['purchase_requests']) == 0