from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework.response import Response
from rest_framework import status
from .models import PurchaseRequest, Decision

User = get_user_model()
PURCHASE_REQUEST_URL = reverse('purchase-request-list-create')

class PurchaseRequestTestCase(APITestCase):
    client: APIClient
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
        
        _ = PurchaseRequest.objects.create(
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
        _ = PurchaseRequest.objects.create(
            title="Finance Request 1",
            amount=1500,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING
        )
        
        _ = PurchaseRequest.objects.create(
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
        assert response_json['data']['size'] == 0
        assert len(response_json['data']['purchase_requests']) == 0

    def test_staff_can_retrieve_own_purchase_request(self):
        """Staff user should be able to retrieve their own purchase request"""
        # Update staff user with full_name
        self.staff_user.full_name = 'Staff Test User' 
        self.staff_user.save()

        # Create a purchase request
        pr = PurchaseRequest.objects.create(
            title="My Purchase Request",
            description="Test description",
            amount=5000,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING,
            proforma="https://example.com/proforma.pdf",
            receipt="https://example.com/receipt.pdf",
            purchase_order="https://example.com/po.pdf"
        )

        detail_url = reverse('purchase-request-retrieve', kwargs={'pk': pr.id})
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(detail_url)

        assert response.status_code == status.HTTP_200_OK 
        response_json = response.json() 
        
        assert response_json['status'] == 'success'
        assert response_json['message'] == 'Purchase request retrieved successfully'
        assert 'data' in response_json
        assert 'purchase_request' in response_json['data']
        
        # Check all fields are present
        pr_data = response_json['data']['purchase_request']
        assert pr_data['id'] == str(pr.id)
        assert pr_data['title'] == pr.title
        assert pr_data['description'] == pr.description
        assert pr_data['amount'] == pr.amount
        assert pr_data['status'] == pr.status
        assert pr_data['created_by'] == self.staff_user.full_name 
        assert pr_data['proforma'] == pr.proforma
        assert pr_data['receipt'] == pr.receipt
        assert pr_data['purchase_order'] == pr.purchase_order
        assert 'created_at' in pr_data

    def test_staff_cannot_retrieve_other_user_purchase_request(self):
        """Staff user should not be able to retrieve another user's purchase request"""
        # Create another staff user
        other_staff_user = User.objects.create_user(
            email='otherstaff@test.com',
            password='StrongPassword123',
            username='otherstaffuser',
            full_name='Other Staff User',
            role='staff'
        )

        # Create a purchase request for the other staff user
        pr = PurchaseRequest.objects.create(
            title="Other User Request",
            description="Another user's request",
            amount=3000,
            created_by=other_staff_user,
            status=PurchaseRequest.Status.PENDING
        )

        detail_url = reverse('purchase-request-retrieve', kwargs={'pk': pr.id})
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(detail_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN 

    def test_approver_can_retrieve_any_purchase_request(self):
        """Approver user should be able to retrieve any purchase request"""
        # Create approver user
        approver = User.objects.create_user(
            email='approver@test.com',
            password='StrongPassword123',
            username='approveruser',
            full_name='Approver User',
            role='approver-level-1'
        )

        # Create a purchase request by staff user
        pr = PurchaseRequest.objects.create(
            title="Request for Approval",
            description="Needs approval",
            amount=7500,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING
        )

        detail_url = reverse('purchase-request-retrieve', kwargs={'pk': pr.id})
        self.client.force_authenticate(user=approver)
        response = self.client.get(detail_url)

        assert response.status_code == status.HTTP_200_OK 
        response_json = response.json() 
        
        assert response_json['status'] == 'success'
        pr_data = response_json['data']['purchase_request']
        assert pr_data['id'] == str(pr.id)
        assert pr_data['title'] == pr.title

    def test_finance_can_retrieve_any_purchase_request(self):
        """Finance user should be able to retrieve any purchase request"""
        # Create finance user
        finance_user = User.objects.create_user(
            email='finance@test.com',
            password='StrongPassword123',
            username='financeuser',
            full_name='Finance User',
            role='finance'
        )

        # Create a purchase request by staff user
        pr = PurchaseRequest.objects.create(
            title="Finance Review Request",
            description="Finance review needed",
            amount=10000,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.APPROVED
        )

        detail_url = reverse('purchase-request-retrieve', kwargs={'pk': pr.id})
        self.client.force_authenticate(user=finance_user)
        response = self.client.get(detail_url)

        assert response.status_code == status.HTTP_200_OK 
        response_json = response.json() 
        
        assert response_json['status'] == 'success'
        pr_data = response_json['data']['purchase_request']
        assert pr_data['id'] == str(pr.id)
        assert pr_data['title'] == pr.title
        assert pr_data['status'] == PurchaseRequest.Status.APPROVED

    def test_retrieve_nonexistent_purchase_request_returns_404(self):
        """Retrieving a non-existent purchase request should return 404"""
        import uuid
        non_existent_id = uuid.uuid4()

        detail_url = reverse('purchase-request-retrieve', kwargs={'pk': non_existent_id})
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(detail_url)

        assert response.status_code == status.HTTP_404_NOT_FOUND 

    def test_retrieve_purchase_request_response_structure(self):
        """Test that retrieve response contains all required fields"""
        # Update staff user with full_name
        self.staff_user.full_name = 'Staff Test User' 
        self.staff_user.save()

        # Create a purchase request with all fields
        pr = PurchaseRequest.objects.create(
            title="Complete Request",
            description="Complete description with all details",
            amount=15000,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING,
            proforma="https://example.com/proforma.pdf",
            receipt=None,
            purchase_order="https://example.com/po.pdf"
        )

        detail_url = reverse('purchase-request-retrieve', kwargs={'pk': pr.id})
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(detail_url)

        assert response.status_code == status.HTTP_200_OK 
        response_json = response.json() 
        
        # Check response structure
        assert 'status' in response_json
        assert 'message' in response_json
        assert 'data' in response_json
        assert 'purchase_request' in response_json['data']
        
        # Check all purchase request fields
        pr_data = response_json['data']['purchase_request']
        required_fields = [
            'id', 'title', 'description', 'amount', 'status',
            'created_at', 'created_by', 'proforma', 'receipt', 'purchase_order'
        ]
        
        for field in required_fields:
            assert field in pr_data, f"Field '{field}' is missing in response"
        
        # Verify field values match
        assert pr_data['id'] == str(pr.id)
        assert pr_data['title'] == pr.title
        assert pr_data['description'] == pr.description
        assert pr_data['amount'] == pr.amount
        assert pr_data['status'] == pr.status
        assert pr_data['created_by'] == self.staff_user.full_name 
        assert pr_data['proforma'] == pr.proforma
        assert pr_data['receipt'] == pr.receipt
        assert pr_data['purchase_order'] == pr.purchase_order

    def test_retrieve_purchase_request_with_null_fields(self):
        """Test retrieving purchase request with null/empty optional fields"""
        # Create purchase request with minimal fields
        pr = PurchaseRequest.objects.create(
            title="Minimal Request",
            description=None,
            amount=500,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING,
            proforma=None,
            receipt=None,
            purchase_order=None
        )

        detail_url = reverse('purchase-request-retrieve', kwargs={'pk': pr.id})
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(detail_url)

        assert response.status_code == status.HTTP_200_OK 
        response_json = response.json() 
        
        pr_data = response_json['data']['purchase_request']
        assert pr_data['description'] is None or pr_data['description'] == ''
        assert pr_data['proforma'] is None or pr_data['proforma'] == ''
        assert pr_data['receipt'] is None or pr_data['receipt'] == ''
        assert pr_data['purchase_order'] is None or pr_data['purchase_order'] == ''


class PurchaseRequestApprovalTestCase(APITestCase):
    """Test cases for purchase request approval functionality."""
    client: APIClient

    def setUp(self):
        """Set up test data for approval tests."""
        # Create staff user who creates purchase requests
        self.staff_user = User.objects.create_user(
            email='staff@test.com',
            password='StrongPassword123',
            username='staffuser',
            full_name='Staff User',
            role='staff'
        )

        # Create approver level 1
        self.approver_level_1 = User.objects.create_user(
            email='approver1@test.com',
            password='StrongPassword123',
            username='approver1',
            full_name='Approver Level 1',
            role='approver-level-1'
        )

        # Create approver level 2
        self.approver_level_2 = User.objects.create_user(
            email='approver2@test.com',
            password='StrongPassword123',
            username='approver2',
            full_name='Approver Level 2',
            role='approver-level-2'
        )

        # Create another approver level 1 (for testing multiple approvers)
        self.approver_level_1_alt = User.objects.create_user(
            email='approver1alt@test.com',
            password='StrongPassword123',
            username='approver1alt',
            full_name='Approver Level 1 Alt',
            role='approver-level-1'
        )

        # Create finance user (should not be able to approve)
        self.finance_user = User.objects.create_user(
            email='finance@test.com',
            password='StrongPassword123',
            username='financeuser',
            full_name='Finance User',
            role='finance'
        )

        # Create normal user (should not be able to approve)
        self.normal_user = User.objects.create_user(
            email='user@test.com',
            password='StrongPassword123',
            username='normaluser',
            full_name='Normal User',
            role='user'
        )

        # Create a purchase request with default approval levels
        self.purchase_request = PurchaseRequest.objects.create(
            title="Test Purchase Request",
            description="Test description for approval",
            amount=5000,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING
        )

    def test_approver_level_1_can_approve_purchase_request(self):
        """Approver level 1 should be able to approve a purchase request."""
        decision_url = reverse('approve-purchase-request', kwargs={'pk': self.purchase_request.id})
        self.client.force_authenticate(user=self.approver_level_1)
        
        decision_data = {
            'comment': 'Looks good, approved'
        }
        
        response = self.client.post(decision_url, decision_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED 
        response_json = response.json() 
        assert response_json['status'] == 'success'
        assert response_json['message'] == 'Purchase Approved Successfully'
        assert 'data' in response_json
        assert 'decision' in response_json['data']
        
        # Verify decision was created
        decision = Decision.objects.get(
            purchase_request=self.purchase_request,
            approver=self.approver_level_1
        )
        assert decision.decision == Decision.DecisionType.APPROVED
        assert decision.approval_level == 'approver-level-1'
        assert decision.comment == 'Looks good, approved'
        
        # Verify purchase request status is still PENDING (not all levels approved yet)
        self.purchase_request.refresh_from_db()
        assert self.purchase_request.status == PurchaseRequest.Status.PENDING

    def test_approver_level_2_can_approve_after_level_1(self):
        """Approver level 2 should be able to approve after level 1 has approved."""
        # First, level 1 approves
        decision_url = reverse('approve-purchase-request', kwargs={'pk': self.purchase_request.id})
        self.client.force_authenticate(user=self.approver_level_1)
        
        decision_data = {
            'comment': 'Level 1 approval'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED 
        
        # Now level 2 approves
        self.client.force_authenticate(user=self.approver_level_2)
        decision_data = {
            'comment': 'Level 2 approval'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED 
        
        # Verify both decisions exist
        assert Decision.objects.filter(
            purchase_request=self.purchase_request,
            approver=self.approver_level_1
        ).exists()
        assert Decision.objects.filter(
            purchase_request=self.purchase_request,
            approver=self.approver_level_2
        ).exists()
        
        # Verify purchase request status is now APPROVED (all levels approved)
        self.purchase_request.refresh_from_db()
        assert self.purchase_request.status == PurchaseRequest.Status.APPROVED

    def test_approver_level_2_cannot_approve_before_level_1(self):
        """Approver level 2 should not be able to approve before level 1."""
        decision_url = reverse('approve-purchase-request', kwargs={'pk': self.purchase_request.id})
        self.client.force_authenticate(user=self.approver_level_2)
        
        decision_data = {
            'comment': 'Trying to approve before level 1'
        }
        
        response = self.client.post(decision_url, decision_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST  
        response_json = response.json()  
        assert 'Level 1 must make decision before level 2 can approve' in str(response_json)
        
        # Verify no decision was created
        assert not Decision.objects.filter(
            purchase_request=self.purchase_request,
            approver=self.approver_level_2
        ).exists()
        
        # Verify purchase request status is still PENDING
        self.purchase_request.refresh_from_db()
        assert self.purchase_request.status == PurchaseRequest.Status.PENDING

    def test_approver_can_reject_purchase_request(self):
        """Approver should be able to reject a purchase request."""
        decision_url = reverse('reject-purchase-request', kwargs={'pk': self.purchase_request.id})
        self.client.force_authenticate(user=self.approver_level_1)
        
        decision_data = {
            'comment': 'Does not meet requirements'
        }
        
        response = self.client.post(decision_url, decision_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED  
        
        # Verify decision was created
        decision = Decision.objects.get(
            purchase_request=self.purchase_request,
            approver=self.approver_level_1
        )
        assert decision.decision == Decision.DecisionType.REJECTED
        assert decision.comment == 'Does not meet requirements'
        
        # Verify purchase request status is immediately REJECTED
        self.purchase_request.refresh_from_db()
        assert self.purchase_request.status == PurchaseRequest.Status.REJECTED

    def test_rejection_immediately_changes_status(self):
        """When any approver rejects, status should change to REJECTED immediately."""
        decision_url = reverse('reject-purchase-request', kwargs={'pk': self.purchase_request.id})
        self.client.force_authenticate(user=self.approver_level_1)
        
        decision_data = {
            'comment': 'Rejected at level 1'
        }
        
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED  
        
        # Verify status changed immediately
        self.purchase_request.refresh_from_db()
        assert self.purchase_request.status == PurchaseRequest.Status.REJECTED
        
        # Verify that level 2 cannot approve after rejection
        decision_url = reverse('approve-purchase-request', kwargs={'pk': self.purchase_request.id})
        self.client.force_authenticate(user=self.approver_level_2)
        decision_data = {
            'comment': 'Trying to approve after rejection'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST  
        assert 'already been rejected' in str(response.json())  

    def test_non_approver_cannot_approve(self):
        """Non-approver users should not be able to approve purchase requests."""
        decision_url = reverse('approve-purchase-request', kwargs={'pk': self.purchase_request.id})
        
        # Test with staff user
        self.client.force_authenticate(user=self.staff_user)
        decision_data = {
            'comment': 'Staff trying to approve'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN  
        
        # Test with finance user
        self.client.force_authenticate(user=self.finance_user)
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN  
        
        # Test with normal user
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN  

    def test_approver_cannot_approve_twice(self):
        """An approver should not be able to approve the same purchase request twice."""
        decision_url = reverse('approve-purchase-request', kwargs={'pk': self.purchase_request.id})
        self.client.force_authenticate(user=self.approver_level_1)
        
        decision_data = {
            'comment': 'First approval'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED  
        
        # Try to approve again
        decision_data = {
            'comment': 'Second approval attempt'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST 
        assert 'already made a decision' in str(response.json())  
        
        # Verify only one decision exists
        decisions = Decision.objects.filter(
            purchase_request=self.purchase_request,
            approver=self.approver_level_1
        )
        assert decisions.count() == 1

    def test_cannot_approve_already_approved_request(self):
        """Should not be able to approve a purchase request that is already fully approved."""
        decision_url = reverse('approve-purchase-request', kwargs={'pk': self.purchase_request.id})
        
        # Level 1 approves
        self.client.force_authenticate(user=self.approver_level_1)
        decision_data = {
            'comment': 'Level 1 approval'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED  
        
        # Level 2 approves (now fully approved)
        self.client.force_authenticate(user=self.approver_level_2)
        decision_data = {
            'comment': 'Level 2 approval'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED  
        
        # Verify status is APPROVED
        self.purchase_request.refresh_from_db()
        assert self.purchase_request.status == PurchaseRequest.Status.APPROVED
        
        # Try to approve again with level 1 (should fail)
        self.client.force_authenticate(user=self.approver_level_1)
        decision_data = {
            'comment': 'Trying to approve already approved request'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST  
        # The service checks status first, so it returns "already been approved" 
        # before checking if the approver already made a decision
        response_json = response.json() 
        error_message = str(response_json)
        assert 'already been approved' in error_message

    def test_cannot_approve_already_rejected_request(self):
        """Should not be able to approve a purchase request that has been rejected."""
        decision_url = reverse('reject-purchase-request', kwargs={'pk': self.purchase_request.id})
        
        # Level 1 rejects
        self.client.force_authenticate(user=self.approver_level_1)
        decision_data = {
            'comment': 'Rejected'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED  
        
        # Verify status is REJECTED
        self.purchase_request.refresh_from_db()
        assert self.purchase_request.status == PurchaseRequest.Status.REJECTED
        
        # Try to approve with level 2 (should fail)
        self.client.force_authenticate(user=self.approver_level_2)
        decision_data = {
            'comment': 'Trying to approve rejected request'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST  
        assert 'already been rejected' in str(response.json())  

    def test_approval_without_comment(self):
        """Approval should work without a comment (comment is optional)."""
        decision_url = reverse('approve-purchase-request', kwargs={'pk': self.purchase_request.id})
        self.client.force_authenticate(user=self.approver_level_1)
        
        decision_data = {
        }
        
        response = self.client.post(decision_url, decision_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED  
        
        # Verify decision was created with null comment
        decision = Decision.objects.get(
            purchase_request=self.purchase_request,
            approver=self.approver_level_1
        )
        assert decision.decision == Decision.DecisionType.APPROVED
        assert decision.comment is None or decision.comment == ''

    def test_approval_response_structure(self):
        """Test that approval response has the correct structure."""
        decision_url = reverse('approve-purchase-request', kwargs={'pk': self.purchase_request.id})
        self.client.force_authenticate(user=self.approver_level_1)
        
        decision_data = {
            'comment': 'Test comment'
        }
        
        response = self.client.post(decision_url, decision_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED  
        
        response_json = response.json()  
        assert 'status' in response_json
        assert 'message' in response_json
        assert 'data' in response_json
        assert 'decision' in response_json['data']
        
        decision_data_response = response_json['data']['decision']
        assert 'id' in decision_data_response
        assert 'decision' in decision_data_response
        assert 'comment' in decision_data_response
        assert 'approval_level' in decision_data_response
        assert 'created_at' in decision_data_response
        assert decision_data_response['decision'] == Decision.DecisionType.APPROVED
        assert decision_data_response['comment'] == 'Test comment'
        assert decision_data_response['approval_level'] == 'approver-level-1'

    def test_approval_with_custom_approval_levels(self):
        """Test approval with custom approval levels."""
        # Create purchase request with only level 2 approval required
        custom_pr = PurchaseRequest.objects.create(
            title="Custom Approval Request",
            description="Only needs level 2 approval",
            amount=3000,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING,
            approval_levels=['approver-level-2']
        )
        
        decision_url = reverse('approve-purchase-request', kwargs={'pk': custom_pr.id})
        
        # Level 1 should not be able to approve (not in approval_levels)
        self.client.force_authenticate(user=self.approver_level_1)
        decision_data = {
            'comment': 'Trying to approve'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN  
        assert 'not required for this purchase request' in str(response.json())  
        
        # Level 2 should be able to approve directly (no level 1 required)
        self.client.force_authenticate(user=self.approver_level_2)
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED  
        
        # Verify status is APPROVED (only one level needed)
        custom_pr.refresh_from_db()
        assert custom_pr.status == PurchaseRequest.Status.APPROVED

    def test_approval_with_multiple_level_1_approvers(self):
        """Test that multiple approvers at the same level can approve different requests."""
        # Create another purchase request
        pr2 = PurchaseRequest.objects.create(
            title="Second Purchase Request",
            description="Another request",
            amount=2000,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING
        )
        
        decision_url_1 = reverse('approve-purchase-request', kwargs={'pk': self.purchase_request.id})
        decision_url_2 = reverse('approve-purchase-request', kwargs={'pk': pr2.id})
        
        # First approver approves first request
        self.client.force_authenticate(user=self.approver_level_1)
        decision_data = {
            'comment': 'First approver'
        }
        response = self.client.post(decision_url_1, decision_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED 
        
        # Second approver approves second request
        self.client.force_authenticate(user=self.approver_level_1_alt)
        response = self.client.post(decision_url_2, decision_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED 
        
        # Verify both decisions exist
        assert Decision.objects.filter(
            purchase_request=self.purchase_request,
            approver=self.approver_level_1
        ).exists()
        assert Decision.objects.filter(
            purchase_request=pr2,
            approver=self.approver_level_1_alt
        ).exists()


    def test_approval_nonexistent_purchase_request(self):
        """Test approval of a non-existent purchase request returns 404."""
        import uuid
        non_existent_id = uuid.uuid4()
        decision_url = reverse('approve-purchase-request', kwargs={'pk': non_existent_id})
        self.client.force_authenticate(user=self.approver_level_1)
        
        decision_data = {
            'comment': 'Approving non-existent request'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND 

    def test_sequential_approval_with_three_levels(self):
        """Test sequential approval with three approval levels."""
        # Create purchase request with three levels
        three_level_pr = PurchaseRequest.objects.create(
            title="Three Level Request",
            description="Needs three approvals",
            amount=10000,
            created_by=self.staff_user,
            status=PurchaseRequest.Status.PENDING,
            approval_levels=['approver-level-1', 'approver-level-2', 'approver-level-3']
        )
        
        # Create approver level 3
        approver_level_3 = User.objects.create_user(
            email='approver3@test.com',
            password='StrongPassword123',
            username='approver3',
            full_name='Approver Level 3',
            role='approver-level-3'
        )
        
        decision_url = reverse('approve-purchase-request', kwargs={'pk': three_level_pr.id})
        
        # Level 1 approves
        self.client.force_authenticate(user=self.approver_level_1)
        decision_data = {
            'comment': 'Level 1'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED 
        three_level_pr.refresh_from_db()
        assert three_level_pr.status == PurchaseRequest.Status.PENDING
        
        # Level 2 approves
        self.client.force_authenticate(user=self.approver_level_2)
        decision_data = {
            'comment': 'Level 2'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED 
        three_level_pr.refresh_from_db()
        assert three_level_pr.status == PurchaseRequest.Status.PENDING
        
        # Level 3 approves (now fully approved)
        self.client.force_authenticate(user=approver_level_3)
        decision_data = {
            'comment': 'Level 3'
        }
        response = self.client.post(decision_url, decision_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED 
        three_level_pr.refresh_from_db()
        assert three_level_pr.status == PurchaseRequest.Status.APPROVED
        
        # Verify all three decisions exist
        assert Decision.objects.filter(
            purchase_request=three_level_pr,
            approver=self.approver_level_1
        ).exists()
        assert Decision.objects.filter(
            purchase_request=three_level_pr,
            approver=self.approver_level_2
        ).exists()
        assert Decision.objects.filter(
            purchase_request=three_level_pr,
            approver=approver_level_3
        ).exists()