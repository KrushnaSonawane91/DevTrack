
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from .views import (
    IssueViewSet,
    ProjectListAPIView,
    DashboardAPIView,
    IssueCommentListCreateAPIView,
)

router = DefaultRouter()
router.register("issues", IssueViewSet, basename="api-issue")

urlpatterns = [
    path("", include(router.urls)),

    path("projects/", ProjectListAPIView.as_view(), name="api-projects"),

    path("dashboard/", DashboardAPIView.as_view(), name="api-dashboard"),

    path(
        "issues/<int:issue_id>/comments/",
        IssueCommentListCreateAPIView.as_view(),
        name="api-issue-comments",
    ),

    path("schema/", SpectacularAPIView.as_view(), name="schema"),

    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
