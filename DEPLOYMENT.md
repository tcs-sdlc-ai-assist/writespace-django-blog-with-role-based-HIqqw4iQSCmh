# Deployment Guide

This document provides detailed instructions for deploying WriteSpace to [Vercel](https://vercel.com/) with a [Neon](https://neon.tech/) PostgreSQL database. It covers environment configuration, database provisioning, build behavior, troubleshooting, and CI/CD considerations.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [1. Provision a Neon PostgreSQL Database](#1-provision-a-neon-postgresql-database)
- [2. Configure Vercel Project](#2-configure-vercel-project)
- [3. Environment Variables Reference](#3-environment-variables-reference)
- [4. Vercel Configuration (`vercel.json`)](#4-vercel-configuration-verceljson)
- [5. Build Script Behavior (`build_files.sh`)](#5-build-script-behavior-build_filessh)
- [6. Static Files](#6-static-files)
- [7. Session Management](#7-session-management)
- [8. Default Admin Account](#8-default-admin-account)
- [9. Custom Domain Setup](#9-custom-domain-setup)
- [10. CI/CD Notes](#10-cicd-notes)
- [11. Troubleshooting](#11-troubleshooting)
  - [Cold Starts](#cold-starts)
  - [Static Files Not Loading](#static-files-not-loading)
  - [Database Migrations Failing](#database-migrations-failing)
  - [CSRF Verification Failed](#csrf-verification-failed)
  - [Allowed Hosts Error](#allowed-hosts-error)
  - [Secret Key Warnings](#secret-key-warnings)
  - [Admin User Not Created](#admin-user-not-created)
  - [Lambda Size Exceeded](#lambda-size-exceeded)
  - [Application Error on First Deploy](#application-error-on-first-deploy)
- [12. Production Security Checklist](#12-production-security-checklist)

---

## Prerequisites

Before deploying, ensure you have:

- A [Vercel](https://vercel.com/) account (free tier is sufficient).
- A [Neon](https://neon.tech/) account for PostgreSQL (free tier provides 0.5 GB storage).
- Your WriteSpace repository hosted on GitHub, GitLab, or Bitbucket.
- A strong, randomly generated `SECRET_KEY` value. Generate one with:

  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

---

## 1. Provision a Neon PostgreSQL Database

WriteSpace uses PostgreSQL in production. [Neon](https://neon.tech/) provides serverless PostgreSQL that pairs well with Vercel's serverless architecture.

### Step-by-Step

1. **Create a Neon account** at [https://neon.tech/](https://neon.tech/).

2. **Create a new project** — choose a name (e.g., `writespace`) and select the region closest to your Vercel deployment (e.g., `us-east-1` for Vercel's default region).

3. **Create a database** — Neon creates a default database named `neondb`. You can rename it or create a new one called `writespace`.

4. **Copy the connection string** from the Neon dashboard. It will look like:

   ```
   postgres://username:password@ep-example-123456.us-east-2.aws.neon.tech/writespace?sslmode=require
   ```

5. **Note the connection string** — you will use this as the `DATABASE_URL` environment variable in Vercel.

### Connection Pooling

Neon supports connection pooling out of the box. For serverless environments like Vercel, use the **pooled connection string** (port `5432` with `-pooler` in the hostname) to avoid exhausting database connections across cold starts:

```
postgres://username:password@ep-example-123456-pooler.us-east-2.aws.neon.tech/writespace?sslmode=require
```

The pooled endpoint is recommended for production deployments on Vercel.

---

## 2. Configure Vercel Project

### Connect Your Repository

1. Log in to [Vercel](https://vercel.com/dashboard).
2. Click **"Add New…" → "Project"**.
3. Import your GitHub/GitLab/Bitbucket repository containing the WriteSpace code.
4. Vercel will auto-detect the project. No framework preset is needed — the `vercel.json` file handles all configuration.

### Set Environment Variables

Navigate to **Settings → Environment Variables** in your Vercel project and add the following:

| Variable                     | Value                                                        | Environment        |
| ---------------------------- | ------------------------------------------------------------ | ------------------- |
| `SECRET_KEY`                 | A strong, randomly generated secret key                      | Production, Preview |
| `DEBUG`                      | `False`                                                      | Production          |
| `DATABASE_URL`               | Your Neon PostgreSQL connection string (pooled recommended)  | Production, Preview |
| `ALLOWED_HOSTS`              | `your-app.vercel.app`                                        | Production          |
| `CSRF_TRUSTED_ORIGINS`       | `https://your-app.vercel.app`                                | Production          |
| `DJANGO_SUPERUSER_USERNAME`  | `admin` (or your preferred admin username)                   | Production          |
| `DJANGO_SUPERUSER_PASSWORD`  | A strong password (change from default!)                     | Production          |
| `DJANGO_SUPERUSER_EMAIL`     | `admin@yourdomain.com`                                       | Production          |

> ⚠️ **Critical:** Never use the default `SECRET_KEY` or `DJANGO_SUPERUSER_PASSWORD` values in production. Both must be changed to strong, unique values.

### Deploy

Click **"Deploy"** or push a commit to your connected branch. Vercel will:

1. Detect the `vercel.json` configuration.
2. Run the build command (`bash build_files.sh`).
3. Deploy the WSGI application as a serverless function.

---

## 3. Environment Variables Reference

| Variable                     | Required | Default                                              | Description                                                                                                    |
| ---------------------------- | -------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `SECRET_KEY`                 | **Yes*** | `insecure-dev-key-change-me`                         | Django secret key for cryptographic signing. **Must** be unique and unpredictable in production.                |
| `DEBUG`                      | No       | `False`                                              | Enables Django debug mode. **Must** be `False` in production. Accepts `True`, `1`, or `yes` (case-insensitive). |
| `DATABASE_URL`               | **Yes*** | SQLite fallback (`db.sqlite3`)                       | PostgreSQL connection string. Format: `postgres://USER:PASS@HOST:PORT/DBNAME?sslmode=require`.                 |
| `ALLOWED_HOSTS`              | No       | `localhost,127.0.0.1`                                | Comma-separated list of hostnames the server will respond to.                                                  |
| `CSRF_TRUSTED_ORIGINS`       | No       | `http://localhost:8000,http://127.0.0.1:8000`        | Comma-separated list of trusted origins for CSRF. **Must** include the scheme (`https://`).                    |
| `DJANGO_SUPERUSER_USERNAME`  | No       | `admin`                                              | Username for the default admin created during build.                                                           |
| `DJANGO_SUPERUSER_PASSWORD`  | No       | `admin`                                              | Password for the default admin. **Change this in production.**                                                 |
| `DJANGO_SUPERUSER_EMAIL`     | No       | `admin@example.com`                                  | Email for the default admin.                                                                                   |

> \* The application will start without these set (using insecure defaults or SQLite), but this is **not safe or functional for production**.

### Multiple Hosts and Origins

For deployments with multiple domains (e.g., custom domain + Vercel default domain):

```
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-app.vercel.app
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://your-app.vercel.app
```

### Preview Deployments

Vercel creates preview deployments for pull requests. Each preview gets a unique URL (e.g., `your-app-git-branch-name.vercel.app`). To support previews:

- Set `ALLOWED_HOSTS` to include `.vercel.app` (with leading dot for wildcard subdomain matching) or add specific preview URLs.
- Set `CSRF_TRUSTED_ORIGINS` to include `https://*.vercel.app` patterns, or configure per-preview environment variables in Vercel.

> **Tip:** Vercel allows you to scope environment variables to specific environments (Production, Preview, Development). Use this to set different `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` for preview vs. production.

---

## 4. Vercel Configuration (`vercel.json`)

The `vercel.json` file at the repository root controls how Vercel builds and routes the application:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "writespace/wsgi.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.12"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "writespace/wsgi.py"
    }
  ],
  "buildCommand": "bash build_files.sh",
  "outputDirectory": ""
}
```

### Key Configuration Details

| Field              | Purpose                                                                                                  |
| ------------------ | -------------------------------------------------------------------------------------------------------- |
| `builds.src`       | Points to the WSGI entry point (`writespace/wsgi.py`), which exposes an `app` callable for Vercel.      |
| `builds.use`       | Uses the `@vercel/python` builder for serverless Python functions.                                       |
| `config.runtime`   | Specifies Python 3.12 as the runtime version.                                                            |
| `config.maxLambdaSize` | Sets the maximum serverless function size to 15 MB (includes dependencies).                          |
| `routes[0]`        | Serves static files directly from the `/static/` directory without hitting the WSGI application.         |
| `routes[1]`        | Routes all other requests to the Django WSGI application.                                                |
| `buildCommand`     | Runs `build_files.sh` during the build phase to install dependencies, collect static files, and migrate. |
| `outputDirectory`  | Empty string — Vercel serves from the repository root.                                                   |

### WSGI Entry Point

The `writespace/wsgi.py` file exposes both `application` (standard WSGI) and `app` (Vercel alias):

```python
application = get_wsgi_application()
app = application  # Vercel expects 'app'
```

The `sys.path.insert()` call in `wsgi.py` ensures Django can locate the `blog` and `accounts` apps regardless of the working directory in the serverless environment.

---

## 5. Build Script Behavior (`build_files.sh`)

The build script runs during every Vercel deployment. It performs four steps in order:

```bash
#!/bin/bash
set -e

echo "=== Installing requirements ==="
pip install -r requirements.txt

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Running database migrations ==="
python manage.py migrate --noinput

echo "=== Creating default admin user ==="
python manage.py create_default_admin
```

### Step-by-Step Breakdown

1. **`pip install -r requirements.txt`** — Installs all Python dependencies (Django, dj-database-url, psycopg2-binary, whitenoise, python-dotenv, gunicorn).

2. **`python manage.py collectstatic --noinput`** — Gathers all static files into the `writespace/staticfiles/` directory. WhiteNoise then serves these files with cache-busting hashes via `CompressedManifestStaticFilesStorage`.

3. **`python manage.py migrate --noinput`** — Applies all pending database migrations to the PostgreSQL database specified by `DATABASE_URL`. This creates or updates all tables (auth, sessions, blog posts, etc.).

4. **`python manage.py create_default_admin`** — Creates the default admin superuser if it does not already exist. Reads credentials from `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`, and `DJANGO_SUPERUSER_EMAIL` environment variables. If the user already exists, it prints a warning and skips creation.

### Important Notes

- The `set -e` flag causes the script to exit immediately if any command fails. If migrations fail, the build will fail and the deployment will not proceed.
- The `manage.py` commands run from the repository root. The `DJANGO_SETTINGS_MODULE` environment variable defaults to `writespace.settings` (set in `manage.py`).
- The build script runs with access to all environment variables configured in Vercel project settings.

---

## 6. Static Files

WriteSpace uses [WhiteNoise](http://whitenoise.evans.io/) to serve static files efficiently in production without a separate web server or CDN.

### How It Works

1. **Collection:** During build, `collectstatic` copies all static files to `writespace/staticfiles/`.
2. **Compression:** `CompressedManifestStaticFilesStorage` generates compressed versions (gzip, brotli) and appends content hashes to filenames for cache busting (e.g., `style.abc123.css`).
3. **Serving:** The `WhiteNoiseMiddleware` in `MIDDLEWARE` intercepts requests to `/static/` and serves files directly from `staticfiles/` with appropriate cache headers.
4. **Routing:** The `vercel.json` route `"/static/(.*)"` ensures static file requests are handled efficiently.

### Static File Settings

From `writespace/settings.py`:

```python
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

### Tailwind CSS

WriteSpace uses Tailwind CSS via CDN (`<script src="https://cdn.tailwindcss.com"></script>` in `base.html`). No local Tailwind build step is required. This approach is suitable for the current project scope but should be replaced with a local Tailwind build for larger production applications.

---

## 7. Session Management

WriteSpace uses Django's **signed cookie session backend**:

```python
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
```

This stores session data directly in the browser cookie, signed with the `SECRET_KEY`. This is critical for serverless deployments because:

- Vercel serverless functions are stateless — there is no persistent filesystem or in-memory session store.
- No database session table is needed, reducing database queries per request.
- Sessions survive across cold starts and different function instances.

### Implications

- **Cookie size limit:** Browsers enforce a ~4 KB cookie size limit. Session data must remain small (user ID, CSRF token, flash messages).
- **SECRET_KEY rotation:** Changing the `SECRET_KEY` invalidates all existing sessions, logging out all users. Plan key rotations carefully.
- **Security:** Session data is signed but not encrypted. Do not store sensitive information in the session beyond what Django stores by default.

---

## 8. Default Admin Account

The `create_default_admin` management command runs during every build. It is idempotent — if the admin user already exists, it skips creation.

### Production Setup

1. Set `DJANGO_SUPERUSER_PASSWORD` to a strong password in Vercel environment variables.
2. Optionally customize `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_EMAIL`.
3. After the first deployment, log in at `https://your-app.vercel.app/accounts/login/` with the configured credentials.
4. The default admin has `is_staff=True` and `is_superuser=True`, granting access to:
   - Admin dashboard (`/accounts/admin/dashboard/`)
   - User management (`/accounts/admin/users/`)
   - Django built-in admin (`/django-admin/`)
   - Full CRUD on all blog posts

### Changing the Admin Password Post-Deployment

To change the admin password after deployment, you can either:

- Update `DJANGO_SUPERUSER_PASSWORD` and delete the existing admin user via the user management page, then redeploy (the build script will recreate the user with the new password).
- Use the Django built-in admin at `/django-admin/` to change the password directly.

---

## 9. Custom Domain Setup

To use a custom domain with your Vercel deployment:

1. **Add the domain** in Vercel: **Settings → Domains → Add**.
2. **Configure DNS** — point your domain's DNS records to Vercel (CNAME or A record as instructed by Vercel).
3. **Update environment variables:**

   ```
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-app.vercel.app
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://your-app.vercel.app
   ```

4. **Redeploy** for the environment variable changes to take effect.

Vercel automatically provisions and renews SSL/TLS certificates for custom domains.

---

## 10. CI/CD Notes

### Automatic Deployments

Vercel automatically deploys on every push to the connected branch:

- **Production deployments** are triggered by pushes to the `main` (or `master`) branch.
- **Preview deployments** are triggered by pushes to any other branch or by pull requests.

### Build Caching

Vercel caches `pip` dependencies between builds. If you update `requirements.txt`, the cache is invalidated and dependencies are reinstalled. To force a clean build, go to **Settings → General → Build & Development Settings** and click **"Clear Build Cache & Redeploy"**.

### Environment Variable Scoping

Vercel supports scoping environment variables to specific environments:

| Scope          | When Used                                      |
| -------------- | ---------------------------------------------- |
| **Production** | Deployments from the production branch (`main`) |
| **Preview**    | Deployments from pull requests and other branches |
| **Development** | Local development via `vercel dev`             |

Use this to set different `DATABASE_URL` values for production vs. preview (e.g., separate Neon branches for preview deployments).

### Neon Database Branching

Neon supports [database branching](https://neon.tech/docs/introduction/branching), which creates isolated copies of your database for preview deployments. This pairs well with Vercel's preview deployment model:

1. Create a Neon branch for each preview environment.
2. Set the branch's connection string as `DATABASE_URL` in the Preview environment scope.
3. Preview deployments get their own isolated database, preventing test data from affecting production.

### Running Tests Before Deployment

Vercel does not natively run tests during the build. To add test execution:

1. **Option A:** Add a test step to `build_files.sh` before the deployment steps:

   ```bash
   echo "=== Running tests ==="
   python manage.py test --noinput
   ```

2. **Option B:** Use a CI service (GitHub Actions, GitLab CI) to run tests before merging to `main`. Only merged code triggers production deployments.

**Recommended approach:** Use Option B. Run tests in CI, and let Vercel handle deployment only after tests pass.

### Example GitHub Actions Workflow

```yaml
name: Test

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: |
          cd writespace
          python manage.py test --noinput
        env:
          SECRET_KEY: test-secret-key-for-ci
          DEBUG: "True"
```

---

## 11. Troubleshooting

### Cold Starts

**Symptom:** The first request after a period of inactivity takes 3–10 seconds to respond.

**Cause:** Vercel serverless functions are shut down after inactivity. The first request triggers a "cold start" that initializes the Python runtime, loads Django, and establishes a database connection.

**Mitigations:**

- Cold starts are inherent to serverless architecture. For most blog applications, this is acceptable.
- Use Neon's pooled connection string to reduce database connection setup time.
- Keep the lambda size small (under 15 MB) to reduce initialization time. The `maxLambdaSize` in `vercel.json` is set to `15mb`.
- Consider Vercel's [Fluid Compute](https://vercel.com/docs/functions/fluid-compute) or cron-based warming if cold starts are unacceptable for your use case.

---

### Static Files Not Loading

**Symptom:** Pages load without CSS styling (unstyled HTML), or static images return 404.

**Possible Causes and Fixes:**

1. **`collectstatic` failed during build:**
   - Check the Vercel build logs for errors during the `collectstatic` step.
   - Ensure `STATIC_ROOT` is set correctly in `settings.py` (`BASE_DIR / "staticfiles"`).

2. **WhiteNoise not in middleware:**
   - Verify `whitenoise.middleware.WhiteNoiseMiddleware` is in `MIDDLEWARE` immediately after `SecurityMiddleware`.

3. **Tailwind CDN blocked:**
   - WriteSpace loads Tailwind CSS from `https://cdn.tailwindcss.com`. If this CDN is blocked by a firewall or content security policy, styles will not load.
   - Check the browser console for blocked resource errors.

4. **Route misconfiguration:**
   - Verify the `/static/(.*)` route exists in `vercel.json` and appears before the catch-all route.

---

### Database Migrations Failing

**Symptom:** Build fails with database-related errors during the migration step.

**Possible Causes and Fixes:**

1. **`DATABASE_URL` not set or incorrect:**
   - Verify the environment variable is set in Vercel project settings.
   - Ensure the connection string format is correct: `postgres://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require`.
   - Test the connection string locally: `python -c "import dj_database_url; print(dj_database_url.parse('YOUR_URL'))"`.

2. **Database does not exist:**
   - Log in to the Neon dashboard and verify the database exists.
   - Create the database if it was accidentally deleted.

3. **Network connectivity:**
   - Neon databases may have IP allowlists. Ensure Vercel's build environment can reach the database. Neon's default configuration allows all IPs.

4. **Migration conflicts:**
   - If you see `InconsistentMigrationHistory` or similar errors, the database state may be out of sync with the migration files.
   - For a fresh deployment, you can reset the Neon database (delete and recreate) and redeploy.

5. **`psycopg2-binary` installation failure:**
   - The `psycopg2-binary` package includes pre-compiled binaries. If the Vercel build environment cannot install it, check that `requirements.txt` specifies `psycopg2-binary` (not `psycopg2`).

---

### CSRF Verification Failed

**Symptom:** Form submissions (login, registration, post creation) fail with "CSRF verification failed. Request aborted."

**Possible Causes and Fixes:**

1. **`CSRF_TRUSTED_ORIGINS` not set or incorrect:**
   - This is the most common cause. Set `CSRF_TRUSTED_ORIGINS` to include your deployment URL with the `https://` scheme:
     ```
     CSRF_TRUSTED_ORIGINS=https://your-app.vercel.app
     ```
   - If using a custom domain, include both the Vercel URL and the custom domain.

2. **Missing scheme in `CSRF_TRUSTED_ORIGINS`:**
   - Django requires the full origin including the scheme. `your-app.vercel.app` will **not** work — it must be `https://your-app.vercel.app`.

3. **Mixed HTTP/HTTPS:**
   - Vercel serves all traffic over HTTPS. Ensure `CSRF_TRUSTED_ORIGINS` uses `https://`, not `http://`.

---

### Allowed Hosts Error

**Symptom:** The application returns "Bad Request (400)" or "DisallowedHost" error.

**Fix:** Add your deployment domain to the `ALLOWED_HOSTS` environment variable:

```
ALLOWED_HOSTS=your-app.vercel.app
```

For multiple domains:

```
ALLOWED_HOSTS=your-app.vercel.app,yourdomain.com,www.yourdomain.com
```

> **Note:** Do not include the scheme (`https://`) in `ALLOWED_HOSTS` — it should be hostnames only.

---

### Secret Key Warnings

**Symptom:** Django logs warnings about an insecure `SECRET_KEY`, or sessions/CSRF tokens behave unexpectedly.

**Fix:** Set a strong, unique `SECRET_KEY` in Vercel environment variables. Generate one with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

The default value (`insecure-dev-key-change-me`) is only for local development and must never be used in production.

---

### Admin User Not Created

**Symptom:** Cannot log in with the default admin credentials after deployment.

**Possible Causes and Fixes:**

1. **Build script did not run:**
   - Check Vercel build logs for the `=== Creating default admin user ===` step.
   - Ensure `build_files.sh` is referenced correctly in `vercel.json` under `buildCommand`.

2. **Database migration failed before admin creation:**
   - The `create_default_admin` command runs after `migrate`. If migrations fail, admin creation is skipped.
   - Fix the migration issue first, then redeploy.

3. **Admin already exists with different password:**
   - The command is idempotent — if a user with the configured username already exists, it skips creation.
   - To reset: delete the admin user via the Neon SQL editor or Django shell, then redeploy.

4. **Wrong credentials:**
   - Verify `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD` in Vercel environment variables match what you are entering on the login page.

---

### Lambda Size Exceeded

**Symptom:** Build fails with "Lambda size exceeds the maximum allowed size of 15 MB."

**Possible Causes and Fixes:**

1. **Too many dependencies:**
   - Review `requirements.txt` and remove unused packages.
   - Use lightweight alternatives where possible (e.g., `psycopg2-binary` instead of compiling `psycopg2` from source).

2. **Large static files:**
   - Static files collected into `staticfiles/` are included in the lambda. Remove unnecessary large files from `writespace/static/`.

3. **Increase the limit:**
   - Update `maxLambdaSize` in `vercel.json` (Vercel's maximum is `50mb` on paid plans, `15mb` on free tier for Python).

---

### Application Error on First Deploy

**Symptom:** Vercel shows "Application Error" or a 500 status code on the first deployment.

**Debugging Steps:**

1. **Check Vercel Function Logs:** Go to your Vercel project → **Deployments** → select the deployment → **Functions** tab → view logs.

2. **Check Build Logs:** Go to **Deployments** → select the deployment → **Build Logs** to see if any build step failed.

3. **Common first-deploy issues:**
   - `DATABASE_URL` not set → Django falls back to SQLite, which does not persist on Vercel's serverless filesystem.
   - `SECRET_KEY` not set → Django uses the insecure default, which may cause issues with signed cookies.
   - `ALLOWED_HOSTS` not set → Django rejects requests from the Vercel domain.

4. **Test locally with production settings:**
   ```bash
   cd writespace
   SECRET_KEY=test DEBUG=False ALLOWED_HOSTS=localhost DATABASE_URL=your-neon-url python manage.py runserver
   ```

---

## 12. Production Security Checklist

Before going live, verify the following:

- [ ] `SECRET_KEY` is set to a strong, unique, randomly generated value.
- [ ] `DEBUG` is set to `False`.
- [ ] `DJANGO_SUPERUSER_PASSWORD` is changed from the default `admin`.
- [ ] `ALLOWED_HOSTS` includes only your production domain(s).
- [ ] `CSRF_TRUSTED_ORIGINS` includes only your production origin(s) with `https://`.
- [ ] `DATABASE_URL` points to your production Neon PostgreSQL instance (pooled endpoint).
- [ ] The Neon database has a strong password and is not using default credentials.
- [ ] Vercel environment variables are scoped appropriately (Production vs. Preview).
- [ ] You have verified the deployment works by logging in and creating a test post.
- [ ] The default admin password has been changed after first login (if not set via environment variable).

---

## Quick Reference

### Deployment Commands (Local Testing)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full build script locally
cd writespace
bash ../build_files.sh

# Or run steps individually
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py create_default_admin

# Start with production-like settings
SECRET_KEY=your-key DEBUG=False ALLOWED_HOSTS=localhost python manage.py runserver
```

### Vercel CLI (Optional)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from local machine
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs your-app.vercel.app
```