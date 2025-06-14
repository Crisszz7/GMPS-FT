#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies (ya lo hace Render, pero es buena práctica)
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
