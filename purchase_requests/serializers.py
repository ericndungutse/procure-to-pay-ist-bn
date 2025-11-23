from rest_framework import serializers
from purchase_requests.services import DecisionManager, ReceiptService
from .models import PurchaseRequest, Decision


class PurchaseRequestListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = PurchaseRequest
        fields = [
            'id',
            'title',
            'amount',
            'status',
            'created_at',
            'created_by_name',
        ]


class PurchaseRequestDetailSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = PurchaseRequest
        fields = [
            'id',
            'title',
            'description',
            'amount',
            'status',
            'created_at',
            'created_by',
            'proforma',
            'receipt',
            'purchase_order',
        ]


class PurchaseRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest
        fields = [
            'id',
            'title',
            'description',
            'amount',
            'proforma',
        ]
        
    def create(self, validated_data):
        request = self.context.get('request')
        if request and getattr(request, 'user', None) and 'created_by' not in validated_data:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class DecisionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating approver decisions on purchase requests."""
    
    class Meta:
        model = Decision
        fields = [
            'id',
            'decision',
            'comment',
            'approval_level',
            'created_at',
        ]
        read_only_fields = ['id', 'approval_level', 'created_at', 'decision']
        
    
    def create(self, validated_data):
        """
        Create a decision using the concurrency-safe manager method.
        """
        request = self.context.get('request')
        purchase_request = self.context.get('purchase_request')
        approver = request.user
        
        decision_type = self.context.get('decision_type')
        comment = validated_data.get('comment', None)
        
        # Use the safe, atomic manager method
        decision = DecisionManager.create_decision(
            purchase_request=purchase_request,
            approver=approver,
            decision_type=decision_type,
            comment=comment
        )
        
        return decision


class ReceiptUploadSerializer(serializers.Serializer):
    """Serializer for updating receipt URL on an approved purchase request."""
    
    receipt_url = serializers.URLField(
        max_length=500,
        help_text="URL of the receipt file uploaded to storage service (e.g., Cloudinary)"
    )
    
    def validate_receipt_url(self, value):
        """Validate receipt URL format."""
        if not value:
            raise serializers.ValidationError("Receipt URL is required.")
        return value
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        receipt_url = validated_data['receipt_url']
        
        # Use the service to perform business logic validation and update
        updated_purchase_request = ReceiptService.upload_receipt(
            purchase_request=instance,
            user=request.user,
            receipt_url=receipt_url
        )
        
        return updated_purchase_request
    
    def save(self):
        purchase_request = self.context.get('purchase_request')
        return self.update(purchase_request, self.validated_data)