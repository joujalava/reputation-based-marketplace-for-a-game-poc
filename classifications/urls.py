from django.urls import path

from .views import ClassificationDetailView, ClassificationListView

app_name = 'classifications'
urlpatterns = [
    path('', ClassificationListView.as_view(), name='classification-list'),
    path('<str:pk>/', ClassificationDetailView.as_view(), name='classification-detail')
]