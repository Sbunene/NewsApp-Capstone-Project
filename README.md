# News Application

A Django-based news application with role-based access control (Reader, Journalist, Editor) and publishing house management.

## Prerequisites

- Python 3.8 or higher
- MariaDB 10.5+ or MySQL 8.0+
- pip (Python package manager)
- Docker (for containerized setup)

## Environment Setup

### 1. Database Configuration

**Install MariaDB/MySQL:**
- **Windows**: Download from [MariaDB.org](https://mariadb.org/download/)
- **Linux**: `sudo apt install mariadb-server mariadb-client`
- **macOS**: `brew install mariadb`

**Create Database and User:**
```sql
CREATE DATABASE newsapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'newsapp_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON newsapp.* TO 'newsapp_user'@'localhost';
FLUSH PRIVILEGES;