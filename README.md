# News Application

A Django-based news application with role-based access control (Reader, Journalist, Editor) and publishing-house support.

This repository contains:
- The Django app under `news/`.
- Sphinx-generated documentation under `docs/_build/html/` (see the `docs` branch for the source and built output).
- Docker support in the `container` branch and a `Dockerfile`/entrypoint in the root.

Quick start (recommended order)
1. Prepare environment variables (`.env`)
2. Install dependencies and run migrations
3. Create groups and a superuser
4. Run locally or via Docker

1) Environment (create `.env` at project root)

Create a `.env` with your DB credentials. Example (do NOT commit real secrets):

```env
# For MariaDB/MySQL (optional)
DB_ENGINE=django.db.backends.mysql
DB_NAME=newsapp
DB_USER=newsapp_user
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306

# Local/dev defaults
DJANGO_DEBUG=True
# If you want an in-memory DB for CI, set CODESPACE_ENV=1 (not recommended for iterative work)
# CODESPACE_ENV=1
```

2) Run locally (venv)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py create_groups
python manage.py createsuperuser
python manage.py runserver
```

3) Docker (container branch)

Build and run the image (the image runs migrations on start via entrypoint):

```bash
docker build -t newsapp .
docker run -p 8000:8000 --env-file .env newsapp
```

4) Docs

Built documentation is available in `docs/_build/html/`. To rebuild locally:

```bash
cd docs
make html
# Open docs/_build/html/index.html in a browser
```

5) Tests

```bash
python manage.py test
```

Notes & security
- Do NOT commit real secrets (DB passwords, API tokens) into this repo. Use `.env` and add it to `.gitignore`.
- If you find secrets committed already, rotate them and remove from history before sharing publicly.

Support
If you'd like, I can:
- Clean up the README further and add step-by-step Docker/compose examples
- Remove secrets from the history (requires force-push and coordination)
- Create a minimal `docker-compose.yml` for local development

-- End of README
- `news.change_newsletter`
- `news.delete_newsletter`
- `news.view_newsletter`
