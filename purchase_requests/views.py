from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from purchase_requests.permissions import IsStaffOrReadOnly
from .models import PurchaseRequest
from .serializers import PurchaseRequestCreateSerializer


class PurchaseRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsStaffOrReadOnly]
    queryset = PurchaseRequest.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PurchaseRequestCreateSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        response = {
            "status": "success",
            "message": "Purchase requests retrieved successfully",
            "data": serializer.data
        }
        
        return Response(response, status=status.HTTP_200_OK)