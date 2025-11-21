from rest_framework import serializers
from .models import PurchaseRequest
from accounts.models import User


class PurchaseRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for PurchaseRequest model.
    """
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    # Read-only fields for display purposes
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approval_levels_display = serializers.CharField(source='get_approval_levels_display', read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = [
            'id',
            'title',
            'description',
            'amount',
            'status',
            'status_display',
            'created_by',
            'created_by_email',
            'created_by_name',
            'proforma',
            'receipt',
            'purchase_order',
            'created_at',
            'approval_levels',
            'approval_levels_display',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        """
        Create a new purchase request.
        If created_by is not provided, use the user from the request context.
        """
        request = self.context.get('request')
        if request and request.user and 'created_by' not in validated_data:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class PurchaseRequestListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing purchase requests.
    """
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = [
            'id',
            'title',
            'amount',
            'status',
            'status_display',
            'created_by',
            'created_by_name',
            'created_at',
        ]

