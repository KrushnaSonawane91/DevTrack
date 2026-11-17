
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from issues.forms import IssueForm
from issues.models import Issue, IssueActivity, IssueComment

from .forms import ProjectForm
from .models import Project


@login_required
def dashboard(request):
    issues = Issue.objects.select_related(
        "project", "reporter", "assignee"
    ).order_by("-created_at")

    if request.user.is_superuser:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(
            Q(owner=request.user) | Q(members=request.user)
        )

    projects = projects.distinct().order_by("-created_at")

    context = {
        "total_projects": projects.count(),
        "projects": projects,
        "total_issues": Issue.objects.count(),
        "open_issues": Issue.objects.filter(
            status=Issue.Status.OPEN
        ).count(),
        "in_progress_issues": Issue.objects.filter(
            status=Issue.Status.IN_PROGRESS
        ).count(),
        "resolved_issues": Issue.objects.filter(
            status=Issue.Status.RESOLVED
        ).count(),
        "closed_issues": Issue.objects.filter(
            status=Issue.Status.CLOSED
        ).count(),
        "low_priority_issues": Issue.objects.filter(
            priority=Issue.Priority.LOW
        ).count(),
        "medium_priority_issues": Issue.objects.filter(
            priority=Issue.Priority.MEDIUM
        ).count(),
        "high_priority_issues": Issue.objects.filter(
            priority=Issue.Priority.HIGH
        ).count(),
        "critical_priority_issues": Issue.objects.filter(
            priority=Issue.Priority.CRITICAL
        ).count(),
        "recent_issues": issues[:5],
    }

    return render(request, "dashboard.html", context)


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, user=request.user)

        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            form.save_m2m()

            messages.success(
                request,
                f'Project "{project.name}" created successfully.',
            )

            return redirect("dashboard")
    else:
        form = ProjectForm(user=request.user)

    return render(
        request,
        "projects/project_form.html",
        {
            "form": form,
            "page_title": "Create Project",
        },
    )


@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Only the project owner or superuser can edit.
    if (
        project.owner_id != request.user.pk
        and not request.user.is_superuser
    ):
        raise PermissionDenied(
            "You do not have permission to edit this project."
        )

    if request.method == "POST":
        form = ProjectForm(
            request.POST,
            instance=project,
            user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                f'Project "{project.name}" updated successfully.',
            )

            return redirect("dashboard")
    else:
        form = ProjectForm(
            instance=project,
            user=request.user,
        )

    return render(
        request,
        "projects/project_form.html",
        {
            "form": form,
            "page_title": "Edit Project",
            "project": project,
        },
    )


@login_required
def issue_list(request):
    issues = Issue.objects.select_related(
        "project", "reporter", "assignee"
    )

    search_query = request.GET.get("search", "").strip()
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")
    issue_type = request.GET.get("issue_type", "")
    sort = request.GET.get("sort", "newest")

    if search_query:
        issues = issues.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(project__name__icontains=search_query)
        )

    if status in Issue.Status.values:
        issues = issues.filter(status=status)

    if priority in Issue.Priority.values:
        issues = issues.filter(priority=priority)

    if issue_type in Issue.IssueType.values:
        issues = issues.filter(issue_type=issue_type)

    if sort == "oldest":
        issues = issues.order_by("created_at", "pk")
    else:
        sort = "newest"
        issues = issues.order_by("-created_at", "-pk")

    paginator = Paginator(issues, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "search": search_query,
        "selected_status": status,
        "selected_priority": priority,
        "selected_issue_type": issue_type,
        "selected_sort": sort,
        "statuses": Issue.Status.choices,
        "priorities": Issue.Priority.choices,
        "issue_types": Issue.IssueType.choices,
    }

    return render(request, "issues/issue_list.html", context)


@login_required
def issue_create(request):
    if request.method == "POST":
        form = IssueForm(request.POST, user=request.user)

        if form.is_valid():
            issue = form.save(commit=False)
            issue.reporter = request.user
            issue.save()

            IssueActivity.objects.create(
                issue=issue,
                user=request.user,
                action=IssueActivity.Action.CREATED,
                message=f'Created issue "{issue.title}".',
            )

            return redirect("issue_detail", pk=issue.pk)
    else:
        form = IssueForm(user=request.user)

    return render(
        request,
        "issues/issue_form.html",
        {"form": form, "page_title": "Create Issue"},
    )


@login_required
def issue_detail(request, pk):
    issue = get_object_or_404(
        Issue.objects.select_related(
            "project", "reporter", "assignee"
        ),
        pk=pk,
    )

    can_manage = (
        issue.reporter_id == request.user.pk
        or issue.project.owner_id == request.user.pk
        or request.user.is_superuser
    )

    comment_error = None

    if request.method == "POST":
        comment_body = request.POST.get("body", "").strip()

        if not comment_body:
            comment_error = "Comment cannot be empty."
        elif len(comment_body) > 5000:
            comment_error = "Comment cannot exceed 5000 characters."
        else:
            IssueComment.objects.create(
                issue=issue,
                author=request.user,
                body=comment_body,
            )

            IssueActivity.objects.create(
                issue=issue,
                user=request.user,
                action=IssueActivity.Action.COMMENTED,
                message="Added a comment.",
            )

            return redirect("issue_detail", pk=issue.pk)

    context = {
        "issue": issue,
        "can_manage": can_manage,
        "comments": issue.comments.select_related("author").all(),
        "activities": issue.activities.select_related("user").all(),
        "comment_error": comment_error,
    }

    return render(request, "issues/issue_detail.html", context)


def _check_issue_permission(request, issue):
    allowed = (
        issue.reporter_id == request.user.pk
        or issue.project.owner_id == request.user.pk
        or request.user.is_superuser
    )

    if not allowed:
        raise PermissionDenied(
            "You do not have permission to modify this issue."
        )


@login_required
def issue_update(request, pk):
    issue = get_object_or_404(
        Issue.objects.select_related("project"),
        pk=pk,
    )

    _check_issue_permission(request, issue)
    old_status = issue.status

    if request.method == "POST":
        form = IssueForm(
            request.POST,
            instance=issue,
            user=request.user,
        )

        if form.is_valid():
            updated_issue = form.save()

            if old_status != updated_issue.status:
                action = IssueActivity.Action.STATUS_CHANGED
                message = (
                    f"Changed status from "
                    f"{Issue.Status(old_status).label} to "
                    f"{updated_issue.get_status_display()}."
                )
            else:
                action = IssueActivity.Action.UPDATED
                message = "Updated issue details."

            IssueActivity.objects.create(
                issue=updated_issue,
                user=request.user,
                action=action,
                message=message,
            )

            return redirect("issue_detail", pk=updated_issue.pk)
    else:
        form = IssueForm(instance=issue, user=request.user)

    return render(
        request,
        "issues/issue_form.html",
        {
            "form": form,
            "issue": issue,
            "page_title": "Edit Issue",
        },
    )


@login_required
def issue_delete(request, pk):
    issue = get_object_or_404(
        Issue.objects.select_related("project"),
        pk=pk,
    )

    _check_issue_permission(request, issue)

    if request.method == "POST":
        issue.delete()
        return redirect("issue_list")

    return render(
        request,
        "issues/issue_confirm_delete.html",
        {"issue": issue},
    )
