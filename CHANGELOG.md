# Changelog

All notable changes to the WriteSpace project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added

#### Public Landing Page (SCRUM-13478)
- Hero section with gradient background and call-to-action buttons.
- Features section highlighting Easy Writing, Share Instantly, and Community Driven.
- Latest posts section displaying the 3 most recent blog posts.
- Call-to-action section for unauthenticated visitors encouraging registration.
- Responsive layout with Tailwind CSS utility classes for mobile, tablet, and desktop.

#### Authentication System (SCRUM-13479)
- Login page with username and password fields and form validation.
- Registration page with username, first name, password, and password confirmation.
- Automatic login after successful registration with redirect to blog list.
- Role-based redirect after login — admin users go to the admin dashboard, regular users go to the blog list.
- Logout via POST request with CSRF protection and redirect to landing page.
- `create_default_admin` management command for automated deployment setup.
- Session management using signed cookies for serverless compatibility.

#### Role-Based Access Control (SCRUM-13479)
- Admin users (`is_staff=True`) have access to the admin dashboard and user management.
- Admin users can create, edit, and delete any blog post on the platform.
- Regular users can create posts and edit or delete only their own posts.
- `@login_required` decorator on all authenticated views.
- `@user_passes_test(staff_required)` decorator on all admin-only views.
- Protection against self-deletion and deletion of the default admin account.

#### Blog CRUD (SCRUM-13478)
- Create new blog posts with title and content fields.
- Read blog posts in a card-based grid layout (blog list) and full article view (blog detail).
- Edit existing blog posts with pre-populated form fields.
- Delete blog posts with confirmation dialog.
- UUID primary keys on all blog posts for non-sequential, URL-safe identifiers.
- Posts ordered by creation date (newest first) with database-level indexes.
- `select_related('author')` on all post querysets to prevent N+1 queries.

#### Admin Dashboard (SCRUM-13480)
- Platform statistics cards: total users, total admins, total posts, and recent post count.
- Quick action links to write a post and manage users.
- Recent posts list with author avatars, dates, and edit/view links.
- Gradient banner with personalized welcome message.

#### User Management (SCRUM-13480)
- User list table (desktop) and card layout (mobile) showing all registered users.
- Create new users with username, first name, password, and role selection (User or Admin).
- Delete users with confirmation dialog and protection rules.
- Role badges (Admin/User) with color-coded styling.
- Date joined display for each user.

#### Avatar System (SCRUM-13478)
- Custom `{% avatar user %}` template tag for role-based inline avatars.
- Crown emoji (👑) with purple background for admin users.
- Book emoji (📖) with blue background for regular users.
- Consistent avatar display across navbar, blog posts, dashboard, and user management.

#### Responsive UI with Tailwind CSS (SCRUM-13478)
- Fully responsive design using Tailwind CSS via CDN.
- Sticky navigation bar with desktop links and mobile hamburger menu.
- Mobile menu toggle with animated icon swap (hamburger ↔ close).
- Card-based layouts with hover effects, shadows, and color-coded top borders.
- Form inputs with consistent focus ring styling across all pages.
- Flash message support with color-coded alert styles (success, error, warning, info).
- Footer with copyright year and branding.

#### Static Files & Deployment (SCRUM-13480)
- Whitenoise middleware for efficient static file serving in production.
- `CompressedManifestStaticFilesStorage` for cache-busting static file hashes.
- `collectstatic` integration in the build script.
- Vercel serverless deployment configuration via `vercel.json`.
- WSGI application with `app` alias for Vercel compatibility.
- ASGI application with `app` alias for alternative deployment targets.
- `build_files.sh` script automating dependency installation, static collection, migrations, and admin creation.
- Environment-based configuration for `SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`.
- PostgreSQL support via `dj-database-url` with SQLite fallback for local development.
- `.env.example` template documenting all required environment variables.