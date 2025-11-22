from .models import PurchaseRequest
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied


class PurchaseRequestService:
    @staticmethod
    def get_filtered_queryset(user):
        queryset = PurchaseRequest.objects.select_related('created_by').all()
        
        # Staff users can only see their own purchase requests
        if user.role == 'staff':
            queryset = queryset.filter(created_by=user)
        
        # Other roles (approver-level-1, approver-level-2, finance) can see all
        return queryset

    @staticmethod
    def get_purchase_request_by_id(user, request_id):
        purchase_request = get_object_or_404(
            PurchaseRequest.objects.select_related('created_by'),
            id=request_id
        )
        
        # Staff users can only see their own purchase requests
        if user.role == 'staff' and purchase_request.created_by != user:
            raise PermissionDenied("You do not have permission to view this purchase request.")
        
        return purchase_request

