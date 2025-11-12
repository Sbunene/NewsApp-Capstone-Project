#!/usr/bin/env bash
set -e

# Run migrations and create groups, then exec the CMD
python manage.py migrate --noinput
python manage.py create_groups || true

# Ensure the command is executed as passed
exec "$@"
