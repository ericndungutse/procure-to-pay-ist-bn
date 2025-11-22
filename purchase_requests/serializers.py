from rest_framework import serializers
from .models import PurchaseRequest
from accounts.models import User


class PurchaseRequestListSerializer(serializers.ModelSerializer):
    """Serializer for listing purchase requests with creator name."""
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