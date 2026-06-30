from django.urls import path

from .views import (
    knowledge_dashboard,
    approve_reference_range_change_view,
    ignore_reference_range_change_view,
)

app_name = "knowledge"

urlpatterns = [
    path(
        "",
        knowledge_dashboard,
        name="knowledge_dashboard",
    ),
    path(
        "reference-ranges/changes/<int:change_id>/approve/",
        approve_reference_range_change_view,
        name="approve_reference_range_change",
    ),
    path(
        "reference-ranges/changes/<int:change_id>/ignore/",
        ignore_reference_range_change_view,
        name="ignore_reference_range_change",
    ),
]