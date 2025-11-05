from django.urls import path

from .views import AddCarryServicePotentialBuyerView, CarryServiceBuyerTradeOutcomeView, CarryServiceCreateView, CarryServiceDeleteView, CarryServiceDetailView, CarryServiceListView, CarryServiceSelectBuyerView, CarryServiceSellerTradeOutcomeView, RemoveCarryServicePotentialBuyerView

app_name = 'carry_services'
urlpatterns = [
    path('', CarryServiceListView.as_view(), name='carry-service-list'),
    path('add-carry-service/', CarryServiceCreateView.as_view(), name='carry-service-create'),
    path('<uuid:pk>/', CarryServiceDetailView.as_view(), name='carry-service-detail'),
    path('<uuid:pk>/add-potential-buyer', AddCarryServicePotentialBuyerView.as_view(), name='carry-service-add-potential-buyer'),
    path('<uuid:pk>/remove-potential-buyer', RemoveCarryServicePotentialBuyerView.as_view(), name='carry-service-remove-potential-buyer'),
    path('<uuid:pk>/select-buyer', CarryServiceSelectBuyerView.as_view(), name='carry-service-select-buyer'),
    path('<uuid:pk>/buyer-outcome', CarryServiceBuyerTradeOutcomeView.as_view(), name='carry-service-buyer-outcome'),
    path('<uuid:pk>/seller-outcome', CarryServiceSellerTradeOutcomeView.as_view(), name='carry-service-seller-outcome'),
    path('<uuid:pk>/delete', CarryServiceDeleteView.as_view(), name='carry-service-delete')
]