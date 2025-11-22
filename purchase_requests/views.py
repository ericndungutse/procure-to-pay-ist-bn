from rest_framework.response import Response
from rest_framework import generics, status
from purchase_requests.permissions import IsStaffOrReadOnly
from .models import PurchaseRequest
from .serializers import PurchaseRequestCreateSerializer, PurchaseRequestListSerializer
from .services import PurchaseRequestService


class PurchaseRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaffOrReadOnly]
    queryset = PurchaseRequest.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PurchaseRequestCreateSerializer
        return PurchaseRequestListSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            return PurchaseRequestService.get_filtered_queryset(self.request.user)
        return super().get_queryset()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        response = {
            "status": "success",
            "message": "Purchase requests retrieved successfully",
            "size": len(serializer.data),
            "data": {
                "size": len(serializer.data),
                "purchase_requests": serializer.data
            }
        }
        
        return Response(response, status=status.HTTP_200_OK)