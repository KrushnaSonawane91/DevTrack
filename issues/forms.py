
from django import forms
from django.db.models import Q

from issues.models import Issue
from project_manager.models import Project


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "title",
            "description",
            "project",
            "assignee",
            "status",
            "priority",
            "issue_type",
        ]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describe the issue...",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is None:
            allowed_projects = Project.objects.none()
        elif user.is_superuser:
            allowed_projects = Project.objects.all()
        else:
            allowed_projects = Project.objects.filter(
                Q(owner=user) | Q(members=user)
            )

            # Keep the existing project available when editing an issue.
            if self.instance and self.instance.pk:
                allowed_projects = Project.objects.filter(
                    Q(pk__in=allowed_projects.values("pk"))
                    | Q(pk=self.instance.project_id)
                )

        self.fields["project"].queryset = (
            allowed_projects.distinct().order_by("name")
        )

        self.fields["assignee"].queryset = (
            self.fields["assignee"].queryset
            .filter(is_active=True)
            .order_by("username")
        )

    def clean_title(self):
        title = self.cleaned_data["title"].strip()

        if not title:
            raise forms.ValidationError("Issue title is required.")

        return title
