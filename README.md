# WriteSpace

A modern, responsive blog platform built with Django and Tailwind CSS. WriteSpace lets writers create, share, and discover blog posts with a clean, distraction-free interface. Features role-based access control, an admin dashboard, and serverless deployment on Vercel.

---

## Tech Stack

| Layer            | Technology                                      |
| ---------------- | ----------------------------------------------- |
| **Backend**      | Python 3.12, Django 5.0+                        |
| **Database**     | PostgreSQL (production), SQLite (local fallback) |
| **Frontend**     | Tailwind CSS via CDN                             |
| **Static Files** | WhiteNoise with compressed manifest storage      |
| **Deployment**   | Vercel (serverless Python)                       |
| **Sessions**     | Signed cookies (serverless-compatible)           |

---

## Features

### Public Landing Page (SCRUM-13478)
- Hero section with gradient background and call-to-action buttons.
- Features section highlighting Easy Writing, Share Instantly, and Community Driven.
- Latest posts section displaying the 3 most recent blog posts.
- Call-to-action section for unauthenticated visitors encouraging registration.
- Fully responsive layout for mobile, tablet, and desktop.

### Authentication System (SCRUM-13479)
- Login page with username/password fields and form validation.
- Registration page with username, first name, password, and password confirmation.
- Automatic login after successful registration with redirect to blog list.
- Role-based redirect after login — admin users go to the admin dashboard, regular users go to the blog list.
- Logout via POST request with CSRF protection and redirect to landing page.
- `create_default_admin` management command for automated deployment setup.

### Role-Based Access Control (SCRUM-13479)
- **Admin users** (`is_staff=True`): access to admin dashboard, user management, and full CRUD on all posts.
- **Regular users**: can create posts and edit/delete only their own posts.
- `@login_required` decorator on all authenticated views.
- `@user_passes_test` decorator on all admin-only views.
- Protection against self-deletion and deletion of the default admin account.

### Blog CRUD (SCRUM-13478)
- Create, read, update, and delete blog posts.
- Card-based grid layout (blog list) and full article view (blog detail).
- UUID primary keys for non-sequential, URL-safe identifiers.
- Posts ordered by creation date (newest first) with database-level indexes.
- `select_related('author')` on all post querysets to prevent N+1 queries.

### Admin Dashboard (SCRUM-13480)
- Platform statistics: total users, total admins, total posts, and recent post count.
- Quick action links to write a post and manage users.
- Recent posts list with author avatars, dates, and edit/view links.

### User Management (SCRUM-13480)
- User list table (desktop) and card layout (mobile) showing all registered users.
- Create new users with username, first name, password, and role selection.
- Delete users with confirmation dialog and protection rules.
- Role badges (Admin/User) with color-coded styling.

### Avatar System (SCRUM-13478)
- Custom `{% avatar user %}` template tag for role-based inline avatars.
- Crown emoji (👑) with purple background for admin users.
- Book emoji (📖) with blue background for regular users.

### Responsive UI (SCRUM-13478)
- Tailwind CSS utility classes for all styling — no custom CSS files.
- Sticky navigation bar with desktop links and mobile hamburger menu.
- Card-based layouts with hover effects, shadows, and color-coded top borders.
- Flash message support with color-coded alert styles.

---

## Folder Structure

```
writespace-blog/
├── .env.example                        # Environment variable template
├── build_files.sh                      # Vercel build script
├── CHANGELOG.md                        # Project changelog
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── vercel.json                         # Vercel deployment configuration
└── writespace/                         # Django project root
    ├── manage.py                       # Django management CLI
    ├── static/
    │   └── images/
    │       └── .gitkeep
    ├── templates/
    │   ├── base.html                   # Base template with navbar, footer, messages
    │   ├── accounts/
    │   │   ├── admin_dashboard.html    # Admin dashboard page
    │   │   ├── login.html              # Login page
    │   │   ├── register.html           # Registration page
    │   │   └── user_management.html    # User management page
    │   └── blog/
    │       ├── blog_detail.html        # Single post view
    │       ├── blog_form.html          # Create/edit post form
    │       ├── blog_list.html          # All posts grid
    │       └── landing_page.html       # Public landing page
    ├── accounts/                       # Accounts app (auth, user management)
    │   ├── __init__.py
    │   ├── admin.py                    # Custom User admin configuration
    │   ├── apps.py
    │   ├── forms.py                    # LoginForm, RegisterForm, CreateUserForm
    │   ├── management/
    │   │   └── commands/
    │   │       └── create_default_admin.py
    │   ├── models.py                   # Uses Django's built-in User model
    │   ├── urls.py
    │   └── views.py                    # Auth views, dashboard, user CRUD
    ├── blog/                           # Blog app (posts)
    │   ├── __init__.py
    │   ├── admin.py                    # Post admin configuration
    │   ├── apps.py
    │   ├── forms.py                    # PostForm (ModelForm)
    │   ├── models.py                   # Post model (UUID PK)
    │   ├── templatetags/
    │   │   ├── __init__.py
    │   │   └── avatar_tags.py          # {% avatar user %} template tag
    │   ├── urls.py
    │   └── views.py                    # Landing page, blog CRUD views
    └── writespace/                     # Django project configuration
        ├── __init__.py
        ├── asgi.py
        ├── settings.py                 # Central settings module
        ├── urls.py                     # Root URL dispatcher
        └── wsgi.py                     # WSGI entry point (Vercel)
```

---

## Local Development Setup

### Prerequisites

- **Python 3.12** or later
- **pip** (Python package manager)
- **PostgreSQL** (optional — SQLite is used as a fallback)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd writespace-blog
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and fill in the values:

```bash
cp .env.example .env
```

Edit `.env` with your local settings:

```dotenv
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://postgres:postgres@localhost:5432/writespace
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

> **Tip:** Generate a secret key with:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

> **Note:** If `DATABASE_URL` is not set, Django will automatically fall back to a local SQLite database (`db.sqlite3`), which requires no additional setup.

### 5. Run Migrations

```bash
cd writespace
python manage.py migrate
```

### 6. Create a Superuser

Use the built-in management command to create a default admin:

```bash
python manage.py create_default_admin
```

This creates an admin user with the following defaults (configurable via environment variables):

| Variable                      | Default             |
| ----------------------------- | ------------------- |
| `DJANGO_SUPERUSER_USERNAME`   | `admin`             |
| `DJANGO_SUPERUSER_PASSWORD`   | `admin`             |
| `DJANGO_SUPERUSER_EMAIL`      | `admin@example.com` |

Alternatively, create a superuser interactively:

```bash
python manage.py createsuperuser
```

### 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 8. Start the Development Server

```bash
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000) in your browser.

---

## Environment Variables

All configuration is driven by environment variables. For local development, set them in a `.env` file. For Vercel deployment, set them in the Vercel project settings.

| Variable                     | Required | Default                                              | Description                                                                 |
| ---------------------------- | -------- | ---------------------------------------------------- | --------------------------------------------------------------------------- |
| `SECRET_KEY`                 | **Yes*** | `insecure-dev-key-change-me`                         | Django secret key. **Must** be set to a unique, unpredictable value in production. |
| `DEBUG`                      | No       | `False`                                              | Set to `True` for local development. **Must** be `False` in production.     |
| `DATABASE_URL`               | No       | SQLite fallback (`db.sqlite3`)                       | PostgreSQL connection string (e.g., `postgres://USER:PASS@HOST:PORT/DB`).   |
| `ALLOWED_HOSTS`              | No       | `localhost,127.0.0.1`                                | Comma-separated list of allowed hostnames.                                  |
| `CSRF_TRUSTED_ORIGINS`       | No       | `http://localhost:8000,http://127.0.0.1:8000`        | Comma-separated list of trusted origins (must include scheme).              |
| `DJANGO_SUPERUSER_USERNAME`  | No       | `admin`                                              | Username for the default admin created by `create_default_admin`.           |
| `DJANGO_SUPERUSER_PASSWORD`  | No       | `admin`                                              | Password for the default admin. **Change this in production.**              |
| `DJANGO_SUPERUSER_EMAIL`     | No       | `admin@example.com`                                  | Email for the default admin.                                                |

> \* The application will start without `SECRET_KEY` set (using the insecure default), but this is **not safe for production**.

---

## Vercel Deployment

WriteSpace is configured for serverless deployment on [Vercel](https://vercel.com/).

### 1. Connect Your Repository

Link your GitHub/GitLab repository to a new Vercel project.

### 2. Set Environment Variables

In the Vercel project settings (**Settings → Environment Variables**), add:

| Variable               | Value                                        |
| ---------------------- | -------------------------------------------- |
| `SECRET_KEY`           | A strong, randomly generated secret key      |
| `DEBUG`                | `False`                                      |
| `DATABASE_URL`         | Your PostgreSQL connection string (e.g., Neon) |
| `ALLOWED_HOSTS`        | `your-app.vercel.app`                        |
| `CSRF_TRUSTED_ORIGINS` | `https://your-app.vercel.app`                |

### 3. Deploy

Vercel will automatically run the build script (`build_files.sh`) which:

1. Installs Python dependencies from `requirements.txt`.
2. Collects static files with `collectstatic`.
3. Runs database migrations.
4. Creates the default admin user (if it doesn't already exist).

### Deployment Configuration

The `vercel.json` file configures:

- **Build**: Uses `@vercel/python` with Python 3.12 runtime, targeting `writespace/wsgi.py`.
- **Routes**: Static files are served directly; all other requests are routed to the WSGI application.
- **Build command**: `bash build_files.sh`.

---

## Usage Notes

### Default Accounts

After running `create_default_admin`, you can log in with:

- **Username:** `admin`
- **Password:** `admin`

> ⚠️ **Change the default admin password immediately in production** by setting `DJANGO_SUPERUSER_PASSWORD` in your environment variables.

### User Roles

| Role          | Permissions                                                                 |
| ------------- | --------------------------------------------------------------------------- |
| **Admin**     | Full access: dashboard, user management, create/edit/delete any post        |
| **User**      | Create posts, edit/delete own posts, browse all posts                       |

### Key URLs

| URL                          | Description                    | Access          |
| ---------------------------- | ------------------------------ | --------------- |
| `/`                          | Public landing page            | Everyone        |
| `/accounts/login/`           | Login page                     | Unauthenticated |
| `/accounts/register/`        | Registration page              | Unauthenticated |
| `/blogs/`                    | All blog posts                 | Authenticated   |
| `/blogs/write/`              | Create a new post              | Authenticated   |
| `/blogs/<uuid>/`             | View a single post             | Authenticated   |
| `/blogs/<uuid>/edit/`        | Edit a post                    | Author or Admin |
| `/blogs/<uuid>/delete/`      | Delete a post (POST only)      | Author or Admin |
| `/accounts/admin/dashboard/` | Admin dashboard                | Admin only      |
| `/accounts/admin/users/`     | User management                | Admin only      |
| `/django-admin/`             | Django built-in admin          | Superuser       |

### Session Management

Sessions use Django's signed cookie backend (`django.contrib.sessions.backends.signed_cookies`), which stores session data in the cookie itself rather than in a database table. This makes the application fully compatible with serverless environments where persistent local storage is not available.

---

## License

This project is proprietary. All rights reserved.