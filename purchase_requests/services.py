from purchase_requests.service.function_invoker_service import FunctionEnvokerService
from .models import PurchaseRequest, Decision
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import transaction, IntegrityError


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



class DecisionManager:
    @staticmethod
    def create_decision(purchase_request, approver, decision_type, comment=None):
        DecisionManager._validate_approver(purchase_request, approver);

        try:
            with transaction.atomic():
                # 1) Lock the purchase request row immediately
                pr = (
                    PurchaseRequest.objects
                    .select_for_update()
                    .get(pk=purchase_request.pk)
                )

                # 2) Re-check status under lock
                if pr.status == PurchaseRequest.Status.APPROVED:
                    raise ValidationError("This purchase request has already been approved.")
                if pr.status == PurchaseRequest.Status.REJECTED:
                    raise ValidationError("This purchase request has already been rejected.")

                # 3) Check if approver already decided (now safe because PR row is locked)
                if Decision.objects.filter(purchase_request=pr, approver=approver).exists():
                    raise ValidationError("You have already made a decision on this purchase request.")

                # 4) Sequential approval check (all previous levels must have APPROVED)
                approver_level_num = int(approver.role.split('-')[-1])
                required_levels_sorted = sorted(
                    pr.approval_levels,
                    key=lambda x: int(x.split('-')[-1])
                )

                for level in required_levels_sorted:
                    level_num = int(level.split('-')[-1])
                    if level_num < approver_level_num:
                        prev_approved = Decision.objects.filter(
                            purchase_request=pr,
                            approval_level=level,
                            decision=Decision.DecisionType.APPROVED
                        ).exists()
                        if not prev_approved:
                            raise ValidationError(
                                f"Level {level_num} must make decision before level {approver_level_num} can approve."
                            )

                # 5) Create decision (unique constraint will prevent duplicates in extreme races)
                decision = Decision.objects.create(
                    purchase_request=pr,
                    approver=approver,
                    decision=decision_type,
                    approval_level=approver.role,
                    comment=comment
                )

                # 6) Update purchase request status if needed
                if decision_type == Decision.DecisionType.REJECTED:
                    pr.status = PurchaseRequest.Status.REJECTED
                    pr.save(update_fields=['status'])
                else:  # APPROVED
                    approved_levels = set(
                        Decision.objects.filter(
                            purchase_request=pr,
                            decision=Decision.DecisionType.APPROVED
                        ).values_list('approval_level', flat=True)
                    )
                    if set(pr.approval_levels) == approved_levels:
                        pr.status = PurchaseRequest.Status.APPROVED
                        pr.save(update_fields=['status'])
                        
                        lambda_fn_payload = DecisionManager._create_lambda_fn_payload(pr)
                        FunctionEnvokerService.envoke_function("FileProcessor", lambda_fn_payload)
                return decision

        except IntegrityError as exc:
            # If a concurrent transaction created the same (purchase_request, approver) record
            # and there's a unique constraint, handle it gracefully.
            raise ValidationError(str(exc)) from exc
    
    @staticmethod
    def _validate_approver(purchase_request, approver):
        if not approver.role.startswith('approver-level-'):
            raise PermissionDenied("Only approvers can make decisions on purchase requests.")
        if approver.role not in purchase_request.approval_levels:
            raise PermissionDenied("Your approval level is not required for this purchase request.")
        
    @staticmethod   
    def _create_lambda_fn_payload(pr):
        return {
            "id": str(pr.id),
            "title": pr.title,
            "description": pr.description,
            "amount": pr.amount,
            "proforma": pr.proforma
        }
        


class ReceiptService:
    @staticmethod
    def upload_receipt(purchase_request, user, receipt_url):
        # Validate user owns the purchase request
        if purchase_request.created_by != user:
            raise PermissionDenied("You can only upload receipts for purchase requests you created.")
        
        # Validate purchase request is approved
        if purchase_request.status != PurchaseRequest.Status.APPROVED:
            raise ValidationError(
                f"Cannot upload receipt. Purchase request must be approved. Current status: {purchase_request.get_status_display()}"
            )
        
        # Update receipt URL
        purchase_request.receipt = receipt_url
        purchase_request.save(update_fields=['receipt'])
        
        return purchase_request