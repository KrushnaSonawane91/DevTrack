# DevTrack — Developer Issue Tracker

A Django-based project and issue tracking application that helps development teams organize projects, track issues, collaborate through comments, and monitor progress.

**Built with Python, Django, Django REST Framework, PostgreSQL, Docker, HTML, and CSS.**

[GitHub Repository](https://github.com/KrushnaSonawane91/DevTrack)

## Features

### User Authentication
- User registration and login
- Secure session-based authentication
- Logout functionality

### Project Management
- Create and edit projects
- Assign team members to projects
- View projects you own or participate in
- Project owner-based editing permissions

### Issue Management
- Create, view, edit, and delete issues
- Assign issues to projects and users
- Track issue status and priority
- Categorize issues as bugs, features, or tasks
- Search and filter issues
- Sort issues and navigate paginated results

### Collaboration
- Add comments to issues
- View issue activity history
- Allow authenticated users to view and comment on shared issues
- Restrict issue editing and deletion to authorized users

### Dashboard
- View project and issue statistics
- Monitor issue statuses and priorities
- Access recent issues and project information

### REST API
- Django REST Framework integration
- API endpoints for dashboard, projects, issues, and comments
- Authentication-protected API access
- Session and Basic authentication support

## Technology Stack

| Category | Technologies |
|---|---|
| Backend | Python, Django |
| REST API | Django REST Framework |
| Database | PostgreSQL |
| Frontend | HTML, CSS, JavaScript |
| Containerization | Docker, Docker Compose |
| Testing | Django Test Framework |
| Version Control | Git, GitHub |

## Project Structure

```text
DevTrack/
│
├── accounts/             # User authentication
├── api/                  # REST API
├── config/               # Django project configuration
├── issues/               # Issue models and functionality
├── projects/             # Projects application
├── project_manager/      # Project and dashboard management
├── static/
│   └── css/              # Stylesheets
├── templates/            # HTML templates
│
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
└── .gitignore
```

## Getting Started

### Prerequisites

- Git
- Docker Desktop
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/KrushnaSonawane91/DevTrack.git
cd DevTrack
```

### 2. Configure environment variables

Create a local `.env` file using the variable names and configuration expected by `docker-compose.yml` and Django settings.

Do not commit `.env` or expose database passwords and secret keys.

### 3. Build and start the application

```bash
docker compose up -d --build
```

### 4. Open the application

Visit:

```text
http://127.0.0.1:8000/
```

### 5. Create an administrator account

```bash
docker compose exec web python manage.py createsuperuser
```

Follow the prompts to create your account.

## Running Tests

Run the project-management tests:

```bash
docker compose exec web python manage.py test project_manager
```

Run the complete test suite:

```bash
docker compose exec web python manage.py test
```

The project has successfully passed **33 automated tests** during development.

## API Endpoints

The API includes endpoints for:

| Endpoint | Purpose |
|---|---|
| `/api/dashboard/` | Dashboard information |
| `/api/issues/` | Issue management |
| Project endpoints | Project management |
| Comment endpoints | Issue comments |

API access requires authentication.

## Permissions

- All authenticated users can view and comment on shared issues.
- Issue reporters, project owners, and administrators can edit or delete issues.
- Project owners and administrators can edit projects.
- Project owners can manage their project teams.

## Stopping the Application

```bash
docker compose down
```

This stops the containers without deleting the PostgreSQL data volume.

## Developer

**Krushna Sonawane**

Computer Engineering Graduate | Python Developer

- GitHub: [KrushnaSonawane91](https://github.com/KrushnaSonawane91)
- LinkedIn: [Krushna Sonawane](https://www.linkedin.com/in/krushna-sonawane-223725288/)

---

*DevTrack is a portfolio project developed to demonstrate Django application development, database integration, REST API development, authentication, permissions, Docker, and automated testing.*