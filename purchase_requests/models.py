from django.db import models
from accounts.models import User


class PurchaseRequest(models.Model):
    """
    Purchase Request model representing purchase requests created by staff.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
    
    class ApprovalLevel(models.TextChoices):
        APPROVER_LEVEL_1 = 'approver-level-1', 'Approver Level 1'
        APPROVER_LEVEL_2 = 'approver-level-2', 'Approver Level 2'
    
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
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
    approval_levels = models.CharField(
        max_length=20,
        choices=ApprovalLevel.choices,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'purchase_requests'
        verbose_name = 'Purchase Request'
        verbose_name_plural = 'Purchase Requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
