from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path("", lambda request: redirect("platform_dashboard"), name="home"),
    path("admin/", admin.site.urls),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("reports/", include("reports.urls")),
    path("knowledge/", include("knowledge.urls")),
]