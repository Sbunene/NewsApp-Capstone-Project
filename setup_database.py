"""Database setup script for NewsApp.

This script helps set up the MariaDB/MySQL database for the NewsApp project.
It will:
1. Create the database if it doesn't exist
2. Create a user if needed
3. Grant necessary permissions
4. Provide instructions for environment setup
"""

import subprocess
import sys
import os

def run_mysql_command(command, user='root', password='', database=None):
    """Run a MySQL command using the mysql client."""
    base_cmd = ['mysql', '-u', user]
    if password:
        base_cmd.extend(['-p' + password])
    if database:
        base_cmd.extend(['-D', database])
    
    try:
        process = subprocess.Popen(
            base_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(command)
        return process.returncode, stdout, stderr
    except Exception as e:
        return 1, '', str(e)

def setup_database():
    """Set up the database and user for NewsApp."""
    print("NewsApp Database Setup")
    print("=====================")
    
    # Get database configuration
    db_name = input("Enter database name (default: news_db): ").strip() or 'news_db'
    # Replace spaces and special characters with underscores
    db_name = ''.join(c if c.isalnum() else '_' for c in db_name)
    print(f"Using database name: {db_name}")
    
    db_user = input("Enter database user (default: root): ").strip() or 'root'
    db_password = input("Enter database password: ").strip()
    
    # Create database
    print("\nCreating database...")
    code, out, err = run_mysql_command(
        f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        user=db_user,
        password=db_password
    )
    
    if code != 0:
        print("Error creating database:", err)
        print("\nTroubleshooting steps:")
        print("1. Make sure MariaDB/MySQL is installed and running")
        print("2. Verify your root password")
        print("3. Run these commands in MySQL shell:")
        print(f"   CREATE DATABASE {db_name};")
        print(f"   GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'localhost';")
        print("   FLUSH PRIVILEGES;")
        return
    
    # Grant privileges
    print("\nGranting privileges...")
    code, out, err = run_mysql_command(
        f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'localhost'; FLUSH PRIVILEGES;",
        user=db_user,
        password=db_password
    )
    
    if code != 0:
        print("Error granting privileges:", err)
        return
    
    # Create .env file
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    with open(env_path, 'w') as f:
        f.write(f"""MYSQL_DATABASE={db_name}
MYSQL_USER={db_user}
MYSQL_PASSWORD={db_password}
MYSQL_HOST=localhost
MYSQL_PORT=3306

# Django settings
DJANGO_SECRET_KEY=django-insecure-o2a6)1kgvu165at&$e&g=#f@ura0obl4$oq_8*hs(!n1xs+uz)
DJANGO_DEBUG=True

# Optional: Twitter API credentials for article sharing
TWITTER_BEARER_TOKEN=
""")
    
    print("\nSuccess! Database setup complete.")
    print("\nNext steps:")
    print("1. The .env file has been created with your database settings")
    print("2. Run these Django commands:")
    print("   python manage.py migrate")
    print("   python manage.py create_groups")
    print("   python manage.py create_sample_data")
    print("3. Create a superuser:")
    print("   python manage.py createsuperuser")
    print("\nThen you can run the development server:")
    print("python manage.py runserver")

if __name__ == '__main__':
    setup_database()