from .models import PurchaseRequest


class PurchaseRequestService:
    @staticmethod
    def get_filtered_queryset(user):
        queryset = PurchaseRequest.objects.select_related('created_by').all()
        
        # Staff users can only see their own purchase requests
        if user.role == 'staff':
            queryset = queryset.filter(created_by=user)
        
        # Other roles (approver-level-1, approver-level-2, finance) can see all
        return queryset

