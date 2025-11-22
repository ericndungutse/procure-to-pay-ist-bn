from django.urls import path
from .views import (PurchaseRequestDecisionView, PurchaseRequestListCreateView,
    PurchaseRequestRetrieveView)

urlpatterns = [
    path('', PurchaseRequestListCreateView.as_view(), name='purchase-request-list-create'),
    path('<uuid:pk>/', PurchaseRequestRetrieveView.as_view(), name='purchase-request-retrieve'),
    path('<uuid:pk>/decide', PurchaseRequestDecisionView.as_view(), name='decide-on-purchase-request'),
]

