from rest_framework import serializers
from .models import PurchaseRequest
from accounts.models import User


class PurchaseRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest
        fields = [
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