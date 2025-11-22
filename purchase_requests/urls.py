from django.urls import path
from .views import PurchaseRequestListCreateView, PurchaseRequestRetrieveView

urlpatterns = [
    path('', PurchaseRequestListCreateView.as_view(), name='purchase-request-list-create'),
    path('<uuid:pk>/', PurchaseRequestRetrieveView.as_view(), name='purchase-request-retrieve'),
]

