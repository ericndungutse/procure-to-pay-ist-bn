from django.urls import path
from .views import PurchaseRequestListCreateView

urlpatterns = [
    path('', PurchaseRequestListCreateView.as_view(), name='purchase-request-list-create'),
]

