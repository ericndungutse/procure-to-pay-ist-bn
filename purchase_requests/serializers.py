from rest_framework import serializers
from .models import PurchaseRequest, Decision
from accounts.models import User


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


class DecisionSerializer(serializers.ModelSerializer):
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
        read_only_fields = ['id', 'approval_level', 'created_at']
    
    def create(self, validated_data):
        """
        Create a decision with purchase_request and approver from context.
        Purchase request comes from URL path variable, approver from request.user.
        """
        request = self.context.get('request')
        purchase_request = self.context.get('purchase_request')
        approver = request.user
        
        # Set purchase_request and approver
        validated_data['purchase_request'] = purchase_request
        validated_data['approver'] = approver
        
        # Set approval_level from approver's role
        validated_data['approval_level'] = approver.role
        
        return super().create(validated_data)