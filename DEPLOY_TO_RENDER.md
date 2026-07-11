# 🚀 Deploy E-Shop to Render.com — Complete Beginner's Guide

> **Who is this for?** If you are a student / fresher and have never deployed a Django app before — this guide is for YOU! I explain every step simply. ☕

---

## 📋 Table of Contents

1. [What is Render & Why Use It?](#1--what-is-render--why-use-it)
2. [What You Need Before Starting](#2--what-you-need-before-starting)
3. [Step 1 — Prepare Your Project for Deployment](#step-1--prepare-your-project-for-deployment)
4. [Step 2 — Create a GitHub Repository](#step-2--create-a-github-repository)
5. [Step 3 — Create a Render Account](#step-3--create-a-render-account)
6. [Step 4 — Create a PostgreSQL Database on Render](#step-4--create-a-postgresql-database-on-render)
7. [Step 5 — Deploy Your Web Service on Render](#step-5--deploy-your-web-service-on-render)
8. [Step 6 — Set Environment Variables](#step-6--set-environment-variables)
9. [Step 7 — Run Migrations & Create Admin User](#step-7--run-migrations--create-admin-user)
10. [Step 8 — Visit Your Live Site!](#step-8--visit-your-live-site)
11. [Common Errors & How to Fix Them](#-common-errors--how-to-fix-them)

---

## 1. 🌐 What is Render & Why Use It?

**Render** is a cloud platform — think of it as a **computer on the internet** that runs your website 24/7 so anyone can visit it.

| Term | Simple Meaning |
|------|---------------|
| **Web Service** | The "computer" on Render that runs your Django project |
| **PostgreSQL** | A database on the cloud (replaces your local `db.sqlite3`) |
| **Environment Variables** | Secret settings (passwords, keys) stored safely on Render |
| **Deploy** | Uploading your code from your PC to Render so it goes live |

> **Why Render?**
> - ✅ Free tier available (server sleeps when unused, wakes up on visit)
> - ✅ PostgreSQL database included (free tier)
> - ✅ Free SSL certificate (HTTPS) automatically
> - ✅ Very easy to use — great for beginners!

---

## 2. 📦 What You Need Before Starting

- [x] Your **E-Shop Django project** (you already have this! ✅)
- [ ] A **GitHub account** — create one free at https://github.com
- [ ] A **Render account** — create one free at https://render.com
- [ ] **Git** installed on your PC
- [ ] **Python 3.12+** installed on your PC
- [ ] Internet connection 🌐

---

## Step 1 — Prepare Your Project for Deployment

We need to add a few files and update `settings.py` so your project works on Render.

### 1.1 — Create `runtime.txt`

This file tells Render which Python version to use.

Create a new file at `e_shop/runtime.txt` with this content:

```
python-3.12
```

> **Why?** Render needs to know what Python version to install. We're using Python 3.12 because it's the latest stable version that works with Django 6.0.

### 1.2 — Update `e_shop/e_shop/settings.py`

Open `e_shop/e_shop/settings.py` and make these changes:

**Step A — Add `import os` at the top (line 13, right after the existing `from pathlib import Path`):**

Find this line:
```python
from pathlib import Path
```

Change it to:
```python
from pathlib import Path
import os
```

> **Why?** We need `os` to read environment variables (secret keys, database passwords, etc.)

---

**Step B — Replace the SECRET_KEY line:**

Find:
```python
SECRET_KEY = 'django-insecure-pe+gqo1(sxdhmf)1r4lu@zm)n82*9!l!pb)lepwdjkv1szhfkq'
```

Replace with:
```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-pe+gqo1(sxdhmf)1r4lu@zm)n82*9!l!pb)lepwdjkv1szhfkq')
```

> **Why?** This lets you set a secret key on Render (secure) while still having a fallback for local development.

---

**Step C — Replace the DEBUG line:**

Find:
```python
DEBUG = True
```

Replace with:
```python
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'
```

> **Why?** On Render, we'll set `DJANGO_DEBUG` to `False` so error details aren't shown to visitors.

---

**Step D — Replace the ALLOWED_HOSTS line:**

Find:
```python
ALLOWED_HOSTS = []
```

Replace with:
```python
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

> **Why?** On Render, we'll set `DJANGO_ALLOWED_HOSTS` to your app's domain name so Django allows connections from there.

---

**Step E — Replace the DATABASES section:**

Find this whole block:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Replace with:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

import dj_database_url
if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(default=os.environ.get('DATABASE_URL'), conn_max_age=600)
```

> **Why?** On Render, we'll set `DATABASE_URL` to connect to the cloud PostgreSQL database. When that env variable exists, we switch from SQLite to PostgreSQL automatically.

But wait — `dj_database_url` is not in your `requirements.txt` yet! We'll add it next.

---

**Step F — Add WhiteNoise to MIDDLEWARE (for serving static files like CSS):**

Find the `MIDDLEWARE` list and add WhiteNoise right after `SecurityMiddleware`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',       # ← ADD THIS LINE
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",  
]
```

> **Why?** WhiteNoise serves your CSS, JavaScript, and images in production. Without it, your site will look broken (no styling).

---

**Step G — Fix the STATIC and MEDIA settings at the bottom of the file:**

Find these lines at the bottom:
```python
STATIC_URL = 'static/'
STATICFILES_DIRS=[BASE_DIR / 'static']
MEDIA_URL='/media/'
MEDIA_ROOT=BASE_DIR / 'media'
```

Replace them with:
```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

> **Why?** `STATIC_ROOT` is where Django collects all static files. `STORAGES` tells Django to use WhiteNoise to compress and serve them efficiently.

---

### 1.3 — Update `e_shop/requirements.txt`

Add `dj-database-url` to your requirements file so Django can read the `DATABASE_URL` environment variable.

Your `e_shop/requirements.txt` should now look like this:

```txt
Django>=6.0,<6.1
pillow>=10.0
requests>=2.31
django-crispy-forms>=2.0
crispy-bootstrap5>=2024.10
django-allauth>=64.0
gunicorn>=22.0
psycopg2-binary>=2.9
whitenoise>=6.0.0
dj-database-url>=2.0
```

> Note: `dj-database-url` is a helper library that reads a single `DATABASE_URL` string and converts it into Django database settings automatically. Very convenient!

---

### 1.4 — Create a `.gitignore` file

This file tells Git which files to NOT upload to GitHub (like your database, Python cache files, etc.).

Create a new file called `.gitignore` in the **project root** (`Recording_project/`) with this content:

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.egg-info/
dist/
build/
*.egg

# Virtual environment
.venv/
venv/
env/

# Database (we'll use PostgreSQL on Render, not SQLite)
*.sqlite3

# Media uploads (user uploaded images)
media/

# IDE
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

# Environment variables file
.env
```

---

### 1.5 — Create a `render.yaml` file (optional but recommended)

This file tells Render exactly how to set up your project automatically. Create it in the **project root** (`Recording_project/`):

```yaml
services:
  - type: web
    name: eshop-django-app
    runtime: python
    repo: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
    plan: free
    region: singapore
    buildCommand: pip install -r e_shop/requirements.txt
    startCommand: gunicorn e_shop.wsgi --chdir e_shop --workers 2 --timeout 120
    envVarGroups:
      - key: django-settings
    domains:
      - eshop-django-app.onrender.com
```

> **Note:** You don't HAVE to create this file. You can also set everything up manually through Render's website (we'll cover that). But having `render.yaml` makes it easier to re-deploy later.

---

## Step 2 — Create a GitHub Repository

Your code needs to be on GitHub so Render can access it.

### 2.1 — Create a new repository on GitHub

1. Go to https://github.com and sign in
2. Click the **+** icon (top right) → **New repository**
3. Give it a name like `e-shop` or `eshop-django`
4. Keep it **Public** (Free plan works with public repos)
5. **DO NOT** check "Add a README" or ".gitignore" (we already have them)
6. Click **Create repository**
7. You'll see a page with instructions. We'll use those next.

### 2.2 — Push your code to GitHub

Open **PowerShell** (or Command Prompt) in the `Recording_project` folder and run:

```powershell
# Initialize Git (only if you haven't already)
git init

# Add all your files
git add .

# Commit them
git commit -m "Initial commit"

# Connect to your GitHub repository (USE YOUR OWN URL from GitHub!)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push your code
git branch -M main
git push -u origin main
```

> If this is your first time using Git, it may ask you to set your name and email:
> ```powershell
> git config --global user.name "Your Name"
> git config --global user.email "your.email@example.com"
> ```

✅ **Your code is now on GitHub!** Go check your repository page to confirm.

---

## Step 3 — Create a Render Account

1. Go to https://dashboard.render.com
2. Click **"Create Account"**
3. Sign up using **GitHub** (easiest — just click the GitHub button)
4. Authorize Render to access your GitHub account
5. You're in! 🎉

---

## Step 4 — Create a PostgreSQL Database on Render

We need a cloud database because SQLite doesn't work on Render (its files get deleted when the server restarts).

1. In your Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Fill in:
   - **Name**: `eshop-database` (or anything you like)
   - **Database**: `eshop_db` (this will be the database name)
   - **User**: `eshop_user` (this will be the database username)
   - **Region**: Choose the one closest to you (e.g., `Singapore` or `Frankfurt`)
   - **Plan**: **Free** ✅
3. Click **"Create Database"**
4. Wait about 2-3 minutes for it to be ready

Once created, you'll see a page with database details. **IMPORTANT — Copy these values somewhere safe:**
- **Internal Database URL** (we'll use this)
- **Password** (you may need this later)

> 💡 **Keep this page open** — we'll need the database URL in Step 6.

---

## Step 5 — Deploy Your Web Service on Render

Now let's put your Django app on the internet!

1. In your Render dashboard, click **"New +"** → **"Web Service"**
2. Click **"Build and deploy from a Git repository"**
3. Connect your GitHub account (if not already connected)
4. Find and select your repository (`e-shop` or whatever you named it)
5. Fill in the details:

| Field | Value |
|-------|-------|
| **Name** | `eshop-django-app` |
| **Region** | Same as your database (e.g., `Singapore`) |
| **Branch** | `main` |
| **Root Directory** | `e_shop` |
| **Runtime** | `Python` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn e_shop.wsgi --workers 2 --timeout 120` |
| **Plan** | **Free** ✅ |

6. Click **"Create Web Service"**

> ⏳ Render will start building your app. This takes **3-5 minutes** the first time. You'll see live logs in the dashboard.

After the build finishes, your app will try to start — but it will fail! **Don't worry**, that's because we haven't set up the environment variables yet. Let's do that next.

---

## Step 6 — Set Environment Variables

Environment variables are like secret settings that your app needs to run on Render.

### 6.1 — Go to your Web Service dashboard

1. In Render, click on your web service (`eshop-django-app`)
2. Click the **"Environment"** tab
3. Click **"Add Environment Variable"**

### 6.2 — Add these variables one by one:

| Key | Value |
|-----|-------|
| `DJANGO_SECRET_KEY` | Generate a secret key (see below) |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `eshop-django-app.onrender.com,localhost` |
| `DATABASE_URL` | Your **Internal Database URL** from Step 4 |

> ⚠️ Replace `eshop-django-app` with YOUR actual app name if you used something different.

### How to Generate a Secret Key:

Open PowerShell and run:
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output — that's your secret key! Paste it as the value for `DJANGO_SECRET_KEY`.

### 6.3 — Save and Redeploy

1. After adding all variables, click **"Save Changes"** (or "Update Environment")
2. Render will automatically redeploy your app
3. Watch the logs — this time it should succeed! ✅

---

## Step 7 — Run Migrations & Create Admin User

The database is empty! We need to create the tables and an admin user.

### 7.1 — Open Shell (Terminal) on Render

1. In your Render web service dashboard, click **"Shell"** (top right area)
2. A terminal will open INSIDE your running app on Render

### 7.2 — Run Migrations

In the Render shell, type:
```bash
python manage.py migrate
```

You should see output like:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying shop.0001_initial... OK
  ...
```

✅ **Database tables created!**

### 7.3 — Create Admin User

In the same shell:
```bash
python manage.py createsuperuser
```

Enter:
- **Username**: `admin` (or anything you like)
- **Email**: your email address
- **Password**: Choose a strong password
- **Password (again)**: type it again

✅ **Admin user created!**

### 7.4 — Collect Static Files

```bash
python manage.py collectstatic --noinput
```

You'll see output like:
```
Copying static files...
128 static files copied to '/opt/render/project/src/e_shop/staticfiles'.
```

✅ **Static files ready!**

### 7.5 — Exit the Shell

Type:
```bash
exit
```

### 7.6 — Restart Your App

1. Go back to your web service dashboard
2. Click the **"Manual Deploy"** button (it might say "Deploy" or have a down arrow ▼)
3. Click **"Clear build cache & deploy"**
4. Wait for the deploy to finish

---

## Step 8 — Visit Your Live Site! 🎉

Your app is now live at:

```
https://eshop-django-app.onrender.com
```

Open this URL in your browser! You should see your E-Shop running on the internet! 🎊

**Admin panel** (to add products):
```
https://eshop-django-app.onrender.com/admin/
```

Login with the admin username and password you created.

---

## 🐛 Common Errors & How to Fix Them

### ❌ Error: "Application Error" or Blank Page

**Fix:** Check the logs in Render dashboard → **"Logs"** tab. Look for the error message.

### ❌ Error: "DisallowedHost"

**Fix:** Go to **Environment** tab and make sure `DJANGO_ALLOWED_HOSTS` includes your app's domain:
```
eshop-django-app.onrender.com,localhost
```
Then redeploy.

### ❌ Error: "Static files not loading" (site looks broken, no CSS)

**Fix:** 
1. Make sure `whitenoise.middleware.WhiteNoiseMiddleware` is in your MIDDLEWARE (after SecurityMiddleware)
2. Open **Shell** and run: `python manage.py collectstatic --noinput`
3. Restart your app

### ❌ Error: "Could not connect to database"

**Fix:**
1. Go to **Environment** tab and check that `DATABASE_URL` is set correctly
2. Make sure your PostgreSQL database is still running (check your Render dashboard)

### ❌ Error: "Module not found" (e.g., `No module named 'dj_database_url'`)

**Fix:** Add the missing package to `e_shop/requirements.txt` and re-deploy.

---

## 📝 How to Deploy Again After Making Changes

Whenever you update your code and want to push changes to the live site:

```powershell
# 1. In your project folder, save your changes
cd D:\Course\ostad\E-Commerce\Recording_project
git add .
git commit -m "Describe what you changed"

# 2. Push to GitHub
git push

# 3. Render will automatically deploy! (Wait ~2-3 minutes)
```

Render automatically deploys whenever you push to GitHub. You can also click **"Manual Deploy"** → **"Deploy latest commit"** in the Render dashboard.

---

## ⚠️ Important Note About Media Files (Product Images)

Render's free tier has an **ephemeral filesystem** — meaning files you upload (like product images) will be **deleted** whenever the server restarts.

**For a real project**, you should use a cloud storage service like **Cloudinary** or **AWS S3** to store images. For now (learning/demo), you can:
- Use image URLs from the internet instead of uploading
- Or accept that images will disappear on restart

This does NOT affect your database or code — only uploaded files.

---

## 💰 Cost Summary

| Resource | Cost |
|----------|------|
| **Render Web Service (Free)** | ✅ Free — server sleeps after 15 min inactivity, wakes on visit |
| **Render PostgreSQL (Free)** | ✅ Free — 1 GB storage |
| **GitHub Account** | ✅ Free |
| **Total** | **$0 — completely free!** 🎉 |

> ⏰ Note: On the free plan, your app "goes to sleep" after 15 minutes of inactivity. When someone visits, it takes 30-60 seconds to wake up. This is normal!

---

## ✅ Deployment Checklist

- [ ] `runtime.txt` created at `e_shop/runtime.txt`
- [ ] `settings.py` updated (SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASES, WhiteNoise)
- [ ] `dj-database-url` added to `requirements.txt`
- [ ] `.gitignore` created
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] PostgreSQL database created on Render
- [ ] Web Service created on Render
- [ ] Environment variables set (DJANGO_SECRET_KEY, DJANGO_DEBUG, DJANGO_ALLOWED_HOSTS, DATABASE_URL)
- [ ] Deploy succeeded (check logs)
- [ ] Migrations run via Shell
- [ ] Superuser created via Shell
- [ ] Static files collected
- [ ] App restarted
- [ ] Site tested in browser ✅

---

> **Congratulations! 🎉** Your E-Shop Django project is now **LIVE on the internet** using Render! Share the link with your friends and teachers! 🌍

> **Need help?** Check Render's official docs: https://render.com/docs/deploy-django
