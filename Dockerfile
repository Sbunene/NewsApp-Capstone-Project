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

# Create an entrypoint that runs migrations on container start (safer than at build time)
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create a non-root user to run the application (security best practice)
RUN useradd -m -r django-user && \
    chown -R django-user /app
USER django-user

# Expose the port Django runs on
EXPOSE 8000

# Use the entrypoint to run migrations and other startup tasks, then run the server
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]