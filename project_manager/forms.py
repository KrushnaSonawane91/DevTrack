
from django import forms
from django.contrib.auth import get_user_model

from .models import Project

User = get_user_model()


class ProjectForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={"size": 5}
        ),
        help_text="Select users who should be able to work on this project.",
    )

    class Meta:
        model = Project
        fields = ["name", "description", "members"]

        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Enter project name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describe your project...",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields["members"].queryset = (
                User.objects.filter(is_active=True)
                .exclude(pk=user.pk)
                .order_by("username")
            )

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError("Project name is required.")

        return name
