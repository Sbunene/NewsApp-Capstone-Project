# News Application

A Django-based news application that allows readers to view articles published by journalists and approved by editors.

**Database:** This project uses **MariaDB/MySQL** (not SQLite) as required by the project specifications.

## Prerequisites

- Python 3.8 or higher
- MariaDB 10.5+ or MySQL 8.0+
- pip (Python package manager)

## Setup Instructions

### 1. Install MariaDB

**Windows:**
```bash
# Download and install MariaDB from: https://mariadb.org/download/
# During installation, set a root password and note the port (default: 3306)
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mariadb-server mariadb-client
sudo systemctl start mariadb
sudo mysql_secure_installation
```

**macOS:**
```bash
brew install mariadb
brew services start mariadb
mysql_secure_installation
```

### 2. Create Database and User

**Option A: Using the automated setup script (Recommended)**
```bash
python setup_database.py
```
This script will guide you through creating the database, user, and `.env` file.

**Option B: Manual setup**
```bash
# Login to MariaDB
mysql -u root -p

# Create database
CREATE DATABASE newsapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (replace 'your_password' with a strong password)
CREATE USER 'newsapp_user'@'localhost' IDENTIFIED BY 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON newsapp.* TO 'newsapp_user'@'localhost';
FLUSH PRIVILEGES;

# Exit
EXIT;
```

### 3. Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies (includes mysqlclient for MariaDB)
pip install -r requirements.txt
```

**Note:** If you encounter issues installing `mysqlclient` on Windows, you may need to:
- Install Microsoft C++ Build Tools from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Or use a pre-built wheel: `pip install mysqlclient‑2.2.7‑cp312‑cp312‑win_amd64.whl`

### 4. Configure Environment Variables

Create a `.env` file in the project root (or use the one created by `setup_database.py`):
```env
MYSQL_DATABASE=newsapp
MYSQL_USER=newsapp_user
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306

DJANGO_SECRET_KEY=django-insecure-o2a6)1kgvu165at&$e&g=#f@ura0obl4$oq_8*hs(!n1xs+uz)
DJANGO_DEBUG=True
```

**Important:** The database settings in `news_app/settings.py` are already configured for MariaDB:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Uses MariaDB/MySQL
        'NAME': 'newsapp',
        'USER': 'newsapp_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Database Migration

```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Initial Groups and Test Data

```bash
# Create user groups (Reader, Journalist, Editor)
python manage.py create_groups

# Optional: Create sample data for testing
python manage.py create_sample_data

# Create a superuser account
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Access the application at: http://127.0.0.1:8000/
Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

- `news/` - Main application directory
  - `models.py` - Database models (CustomUser, Article, Publisher, Newsletter)
  - `views.py` - View functions for handling requests
  - `api_views.py` - REST API views
  - `forms.py` - Forms for data input
  - `tests.py` - Unit tests
  - `urls.py` - URL routing

## Features

- Role-based access control (Reader, Journalist, Editor)
- Article creation and approval workflow
- Email notifications for subscribers
- REST API with authentication
- Comprehensive test coverage

## API Endpoints

- `/api/articles/` - List approved articles
- `/api/articles/<pk>/` - Retrieve single article
- `/api/users/` - List users

## Testing

Run the test suite:
```bash
python manage.py test
```