# AGENTS.md — E-Commarace (Django E-commerce Demo)

## Project layout

- `e_shop/` — Django project root (contains `manage.py`)
- `e_shop/e_shop/` — Django project settings/urls
- `e_shop/shop/` — single Django app (models, views, forms, urls, utils)
- `e_shop/templates/` — templates (base at `templates/base.html`)
- `e_shop/static/` — static assets
- `e_shop/media/` — uploaded product images

## Commands (run from `e_shop/`)

```bash
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py test      # no tests written yet
```

## Key URLs

| Path | View | Notes |
|------|------|-------|
| `/` | home | |
| `/product/` | product_list | supports `?min_price=`, `?max_price=`, `?ratting=`, `?search=` |
| `/product/<slug:slug>/` | product_detail | |
| `/cart/` | cart_detail | login required |
| `/checkout/` | checkout | login required |
| `/payment/{success,fail,cancel}/<order_id>/` | payment callbacks | `@csrf_exempt`, POST from SSLCOMMERZ |
| `/profile/` | profile | login required, `?tab=orders` for order history |
| `/rate/<product_id>/` | rate_product | only for purchased products |
| `/accounts/` | allauth (incl. Google login) | |
| `/admin/` | Django admin | |

## App conventions

- **Namespace**: `shop` — reference as `shop:home`, `shop:product_list`, etc.
- **Forms**: custom `RegistrationForm`, `RatingForm`, `CheckoutForm` in `shop/forms.py`
- **Auth**: custom `login_view`/`register_view`/`logout_view` coexist with allauth
- **Cart**: `Cart` (OneToOne with User) + `CartItem` — created on first add, not session-based
- **Payment**: SSLCOMMERZ sandbox at `sandbox.sslcommerz.com` — keys hardcoded in `settings.py`
- **Email**: console backend (`django.core.mail.backends.console.EmailBackend`) — SMTP settings are placeholders

## Notable quirks

- **Model typos**: `Catagory` (Category), `Ratting` (Rating), `tansaction_id` (transaction) — keep existing names, do not "fix"
- **`settings.py`**: mixed indentation (tabs+spaces on some lines near allauth/SOCIALACCOUNT) — follow existing style
- **`login_url`**: custom views use `/login/` in `@login_required(login_url='/login/')` — not the allauth default
- **`requirements.txt`**: at `e_shop/requirements.txt` — includes gunicorn, psycopg2-binary, whitenoise, dj-database-url, PyJWT
- **`settings.py`** reads `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and `DATABASE_URL` from env vars with local fallbacks
- **WhiteNoise** configured in MIDDLEWARE + STORAGES for production static file serving
- **`.gitignore`** exists at repo root (`__pycache__/`, `*.sqlite3`, `media/`, `.venv/`, etc.)
- **`runtime.txt`** at repo root (`python-3.12.0`) — required by Render
- **No tests** written (`shop/tests.py` is default stub)
- **`DEPLOY_TO_AZURE.md`** and **`DEPLOY_TO_RENDER.md`** have full deployment guides at repo root
- **`render.yaml`** at repo root for Render Blueprint deploy (optional)

## Running the app

1. `python -m venv .venv && .venv\Scripts\activate`
2. `pip install -r e_shop/requirements.txt`
3. `cd e_shop && python manage.py migrate && python manage.py runserver`
