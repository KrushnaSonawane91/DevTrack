
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        login_required(views.dashboard),
        name="dashboard",
    ),

    # Project URLs
    path(
        "projects/create/",
        login_required(views.project_create),
        name="project_create",
    ),

    path(
        "projects/<int:pk>/edit/",
        login_required(views.project_update),
        name="project_update",
    ),

    # Issue URLs
    path(
        "issues/",
        login_required(views.issue_list),
        name="issue_list",
    ),

    path(
        "issues/create/",
        login_required(views.issue_create),
        name="issue_create",
    ),

    path(
        "issues/<int:pk>/",
        login_required(views.issue_detail),
        name="issue_detail",
    ),

    path(
        "issues/<int:pk>/edit/",
        login_required(views.issue_update),
        name="issue_update",
    ),

    path(
        "issues/<int:pk>/delete/",
        login_required(views.issue_delete),
        name="issue_delete",
    ),
]
