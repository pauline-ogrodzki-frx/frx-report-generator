from django.urls import path

from .views import knowledge_dashboard

urlpatterns = [
    path(
        "",
        knowledge_dashboard,
        name="knowledge_dashboard",
    ),
]