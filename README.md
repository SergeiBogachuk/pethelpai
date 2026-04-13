# Pet Help AI MVP

Streamlit MVP for `pethelpai.com`.

## What is included

- registration, sign-in, and password reset flow
- user profile with timezone and notification preferences
- pet records for dogs, cats, and other pets
- care calendar with recurring events and reminder presets
- health log, medications, weight tracking, and expenses
- document storage for Premium users
- subscription screen with free, trial, and premium logic
- basic admin dashboard with users, subscriptions, analytics, and support tickets
- local SQLite persistence for fast MVP iteration

## Run locally

From the workspace root:

```bash
python3 -m streamlit run pethelpai/app.py
```

The app creates its local SQLite database automatically under `data/`.

## Email reminders

The MVP now supports real email reminder delivery over SMTP.

Set these environment variables in Render:

```bash
SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_USERNAME=your-smtp-login
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=hello@pethelpai.com
SMTP_USE_TLS=true
```

How it works right now:

- care events and medication reminders create in-app notifications
- if email reminders are enabled in user settings, the app also queues email reminders
- when the app is opened, it runs a reminder sweep and sends any due pending email reminders
- admins can also run a manual reminder sweep from the admin page

This gives you a real external reminder channel before mobile push notifications are added.

## Logo placement

If you want the app to show your brand logo automatically, put one of these files into:

`assets/`

Supported filenames:

- `assets/logo.svg`
- `assets/logo.png`
- `assets/logo.webp`
- `assets/logo.jpg`
- `assets/logo.jpeg`

The app will auto-detect the first one it finds and use it in the header and sidebar.

## Recommended deploy flow

This workspace contains multiple unrelated projects, so the cleanest production path is:

1. Create a dedicated GitHub repository for the contents of this `pethelpai/` folder.
2. Push only these files into that repo root:
   - `app.py`
   - `engine.py`
   - `storage.py`
   - `styles.py`
   - `requirements.txt`
   - `render.yaml`
   - `.gitignore`
3. Create a Render web service from that GitHub repo.
4. Connect the custom domain `pethelpai.com` in Render.

## Render notes

- Build command: already defined in `render.yaml`
- Start command: already defined in `render.yaml`
- Custom domain: add it in Render first, then copy the DNS records Render gives you into your domain provider

## Current MVP notes

- Notifications are implemented as in-app reminders generated from event and medication schedules.
- Email reminders are supported through SMTP env vars.
- Subscription and payment logic is modeled inside the app for MVP testing.
- The next production step would be moving auth, billing, notifications, and file storage to dedicated services.

## Production recommendation

For the fastest launch, point the root domain directly to the app:

- `pethelpai.com` -> Streamlit app

Later, if you want a fuller marketing experience, split it into:

- `pethelpai.com` -> landing page
- `app.pethelpai.com` -> application
