from django.urls import path

from .views import CraftBuyerTradeOutcomeView, CraftDeleteView, CraftCreateView, CraftDetailView, CraftSelectBuyerView, AddCraftPotentialBuyerView, CraftSellerTradeOutcomeView, RemoveCraftPotentialBuyerView

app_name = 'crafts'
urlpatterns = [
    path('add-craft/', CraftCreateView.as_view(), name='craft-create'),
    path('<uuid:pk>/', CraftDetailView.as_view(), name='craft-detail'),
    path('<uuid:pk>/add-potential-buyer', AddCraftPotentialBuyerView.as_view(), name='craft-add-potential-buyer'),
    path('<uuid:pk>/remove-potential-buyer', RemoveCraftPotentialBuyerView.as_view(), name='craft-remove-potential-buyer'),
    path('<uuid:pk>/select-buyer', CraftSelectBuyerView.as_view(), name='craft-select-buyer'),
    path('<uuid:pk>/buyer-outcome', CraftBuyerTradeOutcomeView.as_view(), name='craft-buyer-outcome'),
    path('<uuid:pk>/seller-outcome', CraftSellerTradeOutcomeView.as_view(), name='craft-seller-outcome'),
    path('<uuid:pk>/delete', CraftDeleteView.as_view(), name='craft-delete')
]