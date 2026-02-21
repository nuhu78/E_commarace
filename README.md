# E-Commarace (Django E-commerce Demo)

E-Commarace is a Django-based e-commerce web application that includes product browsing, category filtering, shopping cart management, checkout, payment gateway redirection, order tracking, and product ratings.

## Features

- User authentication (register, login, logout)
- Product catalog with:
  - Category pages
  - Search
  - Price-range filtering
- Product detail pages with related products
- Product rating and review flow for purchased items
- User-specific shopping cart with quantity updates
- Checkout with shipping/contact details
- Payment flow integration stubs for **SSLCOMMERZ** (sandbox URLs configured)
- User profile page with order history
- Admin panel support through Django admin

## Tech Stack

- Python
- Django
- SQLite (default local database)
- django-crispy-forms + crispy-bootstrap5
- django-allauth (including Google provider)
- Requests (for payment API calls)

## Project Structure

```text
E_commarace/
├── README.md
└── e_shop/
    ├── manage.py
    ├── db.sqlite3
    ├── e_shop/            # Django project settings and root urls
    ├── shop/              # Core app: models, views, forms, urls, utils
    ├── templates/         # Base and shop templates
    ├── static/            # Static assets
    └── media/             # Uploaded product media
```

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd E_commarace
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   > If you don't already have a `requirements.txt`, install the core packages manually:
   ```bash
   pip install django pillow requests django-crispy-forms crispy-bootstrap5 django-allauth
   ```

4. **Run database migrations**
   ```bash
   cd e_shop
   python manage.py migrate
   ```

5. **Create an admin user (optional but recommended)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. Open your browser at:
   - App: `http://127.0.0.1:8000/`
   - Admin: `http://127.0.0.1:8000/admin/`

## Configuration Notes

The project currently uses local defaults in `e_shop/e_shop/settings.py`:

- `DEBUG = True`
- SQLite database (`db.sqlite3`)
- Static/media settings for local development
- SMTP email configuration placeholders
- SSLCOMMERZ sandbox endpoints

Before production usage, you should:

- Move secrets and credentials to environment variables
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Configure real SMTP credentials
- Provide valid SSLCOMMERZ store credentials
- Add production static/media handling

## Main Application Flows

- **Catalog flow:** home → product listing/filtering → product detail
- **Purchase flow:** add to cart → checkout → payment process/success/fail/cancel
- **Post-purchase flow:** profile/order history → rating purchased products

## Helpful Commands

From the `e_shop/` directory:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
python manage.py createsuperuser
python manage.py test
```

## Current Status

This project appears to be a learning/demo implementation and is a strong base for:

- Adding inventory management improvements
- Integrating a complete payment confirmation/validation lifecycle
- Hardening authentication/security for production
- Improving tests and deployment configuration

---

If you want, I can also generate:

- a `requirements.txt`
- an `.env.example`
- a production-ready setup section (Gunicorn + Nginx + PostgreSQL)
