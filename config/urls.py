from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path("", lambda request: redirect("platform_dashboard"), name="home"),
    path("admin/", admin.site.urls),
    path("reports/", include("reports.urls")),
    path("knowledge/", include("knowledge.urls")),
]