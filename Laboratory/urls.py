from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.LaboratoryEquipmentListView.as_view(),
        name="lab_equipment_list",
    ),
]