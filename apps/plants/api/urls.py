from django.urls import path
from apps.plants.api.views.detail import PlantListCreateView, PlantDetailView, ControlConfigView

urlpatterns = [
    path("plants/", PlantListCreateView.as_view(), name="plant-list-create"),
    path("plants/<int:pk>/", PlantDetailView.as_view(), name="plant-detail"),
    path("control/config/", ControlConfigView.as_view(), name="control-config"),
]