
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from project_manager.models import Project

User = get_user_model()


class ProjectManagementTests(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username="projectowner",
            password="TestPass123!",
        )
        self.member = User.objects.create_user(
            username="projectmember",
            password="TestPass123!",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="TestPass123!",
        )
        self.superuser = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="TestPass123!",
        )

        self.project = Project.objects.create(
            name="Test Project",
            description="Project for automated tests",
            owner=self.owner,
        )
        self.project.members.add(self.member)

    def test_project_creation_requires_login(self):
        response = self.client.get(reverse("project_create"))

        self.assertEqual(response.status_code, 302)

    def test_user_can_create_project(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("project_create"),
            {
                "name": "New Project",
                "description": "A newly created project",
                "members": [self.member.pk],
            },
        )

        self.assertEqual(response.status_code, 302)

        project = Project.objects.get(name="New Project")

        self.assertEqual(project.owner, self.owner)
        self.assertIn(self.member, project.members.all())

    def test_project_owner_can_edit_project(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("project_update", args=[self.project.pk]),
            {
                "name": "Updated Project",
                "description": "Updated description",
                "members": [self.member.pk],
            },
        )

        self.assertEqual(response.status_code, 302)

        self.project.refresh_from_db()

        self.assertEqual(self.project.name, "Updated Project")
        self.assertEqual(
            self.project.description,
            "Updated description",
        )

    def test_project_member_cannot_edit_project(self):
        self.client.force_login(self.member)

        response = self.client.get(
            reverse("project_update", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 403)

    def test_unrelated_user_cannot_edit_project(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("project_update", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_edit_project(self):
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("project_update", args=[self.project.pk]),
            {
                "name": "Admin Updated Project",
                "description": "Updated by administrator",
                "members": [self.member.pk],
            },
        )

        self.assertEqual(response.status_code, 302)

        self.project.refresh_from_db()
        self.assertEqual(
            self.project.name,
            "Admin Updated Project",
        )

    def test_dashboard_shows_owned_and_member_projects(self):
        member_project = Project.objects.create(
            name="Member Project",
            owner=self.owner,
        )
        member_project.members.add(self.member)

        Project.objects.create(
            name="Unrelated Project",
            owner=self.other_user,
        )

        self.client.force_login(self.member)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)

        visible_projects = list(response.context["projects"])
        visible_names = [project.name for project in visible_projects]

        self.assertIn("Test Project", visible_names)
        self.assertIn("Member Project", visible_names)
        self.assertNotIn("Unrelated Project", visible_names)
