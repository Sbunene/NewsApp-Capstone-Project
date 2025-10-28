# NewsApp - Django News Application

A comprehensive news application built with Django featuring user roles, article management, and REST API.

## Features

- **User Roles**: Reader, Journalist, Editor with different permissions
- **Article Management**: Create, read, update, delete articles
- **Approval Workflow**: Editors review and approve articles
- **Email Notifications**: Subscribers notified when articles are approved
- **REST API**: JSON API for third-party integration
- **Professional UI**: Modern, responsive design
- **Security**: User authentication and role-based permissions

## Installation

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create sample data: `python manage.py create_sample_data`
7. Create user groups: `python manage.py create_groups`
8. Run development server: `python manage.py runserver`

## User Accounts for Testing

- **Reader**: `admin` / `admin123` - Can view approved articles
- **Journalist**: `tech_journalist` / `test123` - Can create and manage articles
- **Editor**: `sample_editor` / `test123` - Can approve/reject articles

## API Endpoints

- `GET /news/api/articles/` - List all approved articles
- `GET /news/api/articles/{id}/` - Get specific article
- `GET /news/api/users/` - List all users

## Testing

Run the test suite: `python manage.py test`

All 5 tests should pass successfully.

## Project Structure
