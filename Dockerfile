# Use an official Python runtime as a base image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=news_app.docker_settings

# Create and set the working directory
RUN mkdir /app
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the Django project code
COPY . /app/

# Run migrations and create initial data
RUN python manage.py migrate
RUN python manage.py create_groups

# Create a non-root user to run the application (security best practice)
RUN useradd -m -r django-user && \
    chown -R django-user /app
USER django-user

# Expose the port Django runs on
EXPOSE 8000

# Command to run the application - use shell form
CMD python manage.py runserver 0.0.0.0:8000