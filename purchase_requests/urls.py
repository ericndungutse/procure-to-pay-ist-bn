from django.urls import path
from .views import (PurchaseRequestApproveView, PurchaseRequestListCreateView, PurchaseRequestRejectView,
    PurchaseRequestRetrieveView, PurchaseRequestReceiptUploadView, PurchaseOrderMismatchListView)

urlpatterns = [
    path('', PurchaseRequestListCreateView.as_view(), name='purchase-request-list-create'),
    path('<uuid:pk>/', PurchaseRequestRetrieveView.as_view(), name='purchase-request-retrieve'),
    path('<uuid:pk>/approve', PurchaseRequestApproveView.as_view(), name='approve-purchase-request'),
    path('<uuid:pk>/reject', PurchaseRequestRejectView.as_view(), name='reject-purchase-request'),
    path('<uuid:pk>/upload-receipt', PurchaseRequestReceiptUploadView.as_view(), name='upload-receipt'),
    path('mismatches/', PurchaseOrderMismatchListView.as_view(), name='purchase-order-mismatches'),
]

