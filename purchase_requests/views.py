from rest_framework.response import Response
from rest_framework import generics, status
from purchase_requests.permissions import IsStaffOrReadOnly
from .models import PurchaseRequest
from .serializers import (DecisionCreateSerializer, PurchaseRequestCreateSerializer,
    PurchaseRequestDetailSerializer, PurchaseRequestListSerializer)
from .services import PurchaseRequestService
from rest_framework.views import APIView


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


class PurchaseRequestRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsStaffOrReadOnly]
    serializer_class = PurchaseRequestDetailSerializer

    def get_object(self):
        """Get purchase request by ID with access control via service."""
        request_id = self.kwargs.get('pk')
        return PurchaseRequestService.get_purchase_request_by_id(
            self.request.user,
            request_id
        )

    def get(self, request, *args, **kwargs):
        purchase_request = self.get_object()
        serializer = self.get_serializer(purchase_request)
        
        response = {
            "status": "success",
            "message": "Purchase request retrieved successfully",
            "data": {
                "purchase_request": serializer.data
            }
        }
        
        return Response(response, status=status.HTTP_200_OK)
    
class PurchaseRequestDecisionView(APIView):
    def post(self, request, pk):
        # TODO: GETTING PURCHASE SHOULD BE IN SERVICE
        purchase_request = PurchaseRequest.objects.get(pk=pk)
        
        serializer = DecisionCreateSerializer(
            data=request.data,
            context={'request': request, 'purchase_request': purchase_request}
        )
        
        serializer.is_valid(raise_exception=True)
        decision = serializer.save();

        return Response({
            "status": "success",
            "message": "Purchase request approved",
            "data": {
                "decision": DecisionCreateSerializer(decision).data
            }
        }, status=status.HTTP_201_CREATED)