from django.contrib import admin
from django.urls import include, path
from django.urls import include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("project_manager.urls")),
    path("api/", include("api.urls")),
]