# Hôtel La Source (Django)

## Installation locale

```bash
cd /home/runner/work/lasource/lasource/hotel
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Vérifications

```bash
python manage.py check
python manage.py test
```

## Variables d’environnement clés

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DB_ENGINE` (`sqlite` par défaut, `postgresql` en production)
- `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT` (si PostgreSQL)
- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
- `HOTEL_CONTACT_ADDRESS`, `HOTEL_CONTACT_PHONE`
- `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD`
- `USE_X_FORWARDED_PROTO`

## Préparation production

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn hotel.wsgi:application --bind 0.0.0.0:8000
```

Points à configurer côté hébergeur:
- Valeurs de sécurité (`SECURE_*`, cookies secure) à `True`/adaptées
- `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS` du domaine réel
- SMTP réel pour l’envoi d’e-mails
- Rotation des secrets (`SECRET_KEY`, mot de passe SMTP, accès DB)
