# 🚀 DevTrack – Developer Issue Tracker

**DevTrack** is a web-based Developer Issue Tracking System built with Django and PostgreSQL. It helps development teams manage projects, track software issues, collaborate through comments, and monitor issue progress from a centralized dashboard.

The application includes role-based permissions, project management, issue tracking, activity history, and REST API support.

## ✨ Key Features

### 📊 Dashboard
- Overview of total projects and issues.
- Issue statistics based on status.
- Priority-wise issue overview.
- Centralized workspace for users.

### 📁 Project Management
- Create and manage projects.
- Edit project details.
- Add team members to projects.
- View projects based on ownership and membership.

### 🐛 Issue Tracking
- Create, view, update, and delete issues.
- Track issue status and priority.
- Categorize issues by type.
- Search and filter issues.
- Sort and paginate issue lists.
- View detailed issue information.

### 💬 Collaboration
- Add comments to issues.
- View issue activity history.
- Allow team members to collaborate on shared issues.

### 🔐 Authentication & Authorization
- User registration and login.
- Secure logout functionality.
- Login-required access to protected pages.
- Permission-based project and issue management.

### 🔌 REST API
- REST API developed using Django REST Framework.
- API support for dashboard, projects, issues, and comments.
- Authentication using Session and Basic Authentication.
- Protected API endpoints using `IsAuthenticated`.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| Django REST Framework | REST API development |
| PostgreSQL | Database |
| HTML5 | Frontend structure |
| CSS3 | Frontend styling |
| Docker | Containerization |
| Docker Compose | Application and database management |
| Git & GitHub | Version control |

## 📸 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Create Issue
![Create Issue](screenshots/create-issue.png)

### All Issues
![All Issues](screenshots/all-issues.png)

## 🏗️ Project Structure

```text
DevTrack/
│
├── accounts/             # User authentication
├── config/               # Django project configuration
├── issues/               # Issue tracking and comments
├── project_manager/      # Project management
├── projects/             # Project-related functionality
├── templates/            # HTML templates
├── static/
│   └── css/              # CSS stylesheets
│
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Application services
├── requirements.txt      # Python dependencies
├── manage.py             # Django management utility
├── .gitignore
└── README.md
```

## ⚙️ Installation & Setup

### Prerequisites

Make sure you have installed:

- Python
- Docker Desktop
- Git

### 1. Clone the repository

```bash
git clone https://github.com/KrushnaSonawane91/DevTrack.git
```

### 2. Navigate to the project directory

```bash
cd DevTrack
```

### 3. Configure environment variables

Check the project's Docker Compose and Django settings for the required environment variables. Create a local `.env` file with the required values if your configuration uses one.

### 4. Build and start the application

```bash
docker compose up -d --build
```

This starts the Django application and PostgreSQL database using Docker Compose.

### 5. Access the application

Open your browser and visit:

```text
http://127.0.0.1:8000/
```

### 6. Stop the application

```bash
docker compose down
```

## 🔌 API Documentation

DevTrack provides REST API functionality through Django REST Framework.

Available API functionality includes:

- Dashboard statistics
- Project management
- Issue management
- Issue comments

The API uses authentication and permission controls to protect endpoints.

The main API routes include:

```text
/api/dashboard/
/api/issues/
```

Additional project and comment endpoints are provided by the application.

## 🔒 Access Control & Permissions

DevTrack implements permission-based access control.

| Action | Permission |
|---|---|
| View shared issues | Authenticated users |
| Add issue comments | Authenticated users |
| Edit an issue | Reporter, project owner, or admin |
| Delete an issue | Reporter, project owner, or admin |
| Edit a project | Project owner or admin |
| Create a project | Authenticated users |

## 🧪 Testing

The project includes automated tests covering application functionality and permissions.

**Test results:**
- 33 automated tests passed.
- Project management permissions tested.
- Issue management functionality tested.
- Authentication and access controls tested.

Run the test suite using:

```bash
docker compose exec web python manage.py test
```

Check the Django project configuration:

```bash
docker compose exec web python manage.py check
```

## 🎯 Project Objectives

- Build a practical issue tracking application using Django.
- Understand backend development and database integration.
- Implement authentication and authorization.
- Develop REST APIs using Django REST Framework.
- Work with PostgreSQL and Docker.
- Apply automated testing to improve application reliability.

## 👨‍💻 Author

**Krushna Sonawane**

- GitHub: [KrushnaSonawane91](https://github.com/KrushnaSonawane91)
- LinkedIn: [Connect on LinkedIn](https://www.linkedin.com/in/krushna-sonawane-223725288)

---

⭐ If you find this project useful, consider giving it a star!
