from django.db import models
from accounts.models import User
import uuid


def default_approval_levels():
    return ['approver-level-1', 'approver-level-2']

class PurchaseRequest(models.Model):
    """
    Purchase Request model representing purchase requests created by staff.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="Description")
    amount = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchase_requests',
        db_column='created_by'
    )
    proforma = models.URLField(max_length=500, blank=True, null=True)
    receipt = models.URLField(max_length=500, blank=True, null=True)
    purchase_order = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    
    approval_levels = models.JSONField(
        default=default_approval_levels
    )

    class Meta:
        db_table = 'purchase_requests'
        verbose_name = 'Purchase Request'
        verbose_name_plural = 'Purchase Requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class Decision(models.Model):
    """
    Decision model to track approver decisions on purchase requests.
    Tracks which approver at which level made what decision.
    """
    
    class DecisionType(models.TextChoices):
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='decisions',
        db_column='purchase_request_id'
    )
    approver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='decisions',
        db_column='approver_id'
    )
    decision = models.CharField(
        max_length=20,
        choices=DecisionType.choices
    )
    approval_level = models.CharField(
        max_length=20,
        help_text="The approval level at which this decision was made (e.g., 'approver-level-1', 'approver-level-2')"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, help_text="Optional comment from the approver", default="No comment")

    class Meta:
        db_table = 'decisions'
        verbose_name = 'Decision'
        verbose_name_plural = 'Decisions'
        ordering = ['-created_at']
        # Ensure an approver can only make one decision per purchase request
        unique_together = [['purchase_request', 'approver']]

    def __str__(self):
        return f"{self.purchase_request.title} - {self.approver.full_name} - {self.get_decision_display()} ({self.approval_level})"


class PurchaseOrderReceiptMismatch(models.Model):
    """
    Minimal mismatch record matching incoming message payload:

        {
            "purchaseRequestId": "...",
            "result": "mismatch detected, description..."
        }

    We store `purchase_request_id` as a UUID and `result` as a plain string
    describing the verifier output.
        """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_request_id = models.UUIDField()
    result = models.TextField()

    class Meta:
        db_table = 'purchase_order_receipt_mismatches'
        verbose_name = 'Purchase Order / Receipt Mismatch'
        verbose_name_plural = 'Purchase Order / Receipt Mismatches'

    def __str__(self):
        return f"Mismatch for PR {self.purchase_request_id}"