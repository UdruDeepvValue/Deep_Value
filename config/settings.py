import os
from datetime import timedelta
from distutils.util import strtobool

from celery.schedules import crontab

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

SECRET_KEY = os.getenv("SECRET_KEY", "KSAFJOADJFLajsofjsjfaoij0392982323riejfwoiujr89wWEJFWEIO") #os.environ["SECRET_KEY"]
DEBUG = bool(strtobool(os.getenv("FLASK_DEBUG", "false")))

SERVER_NAME = os.getenv(
    "SERVER_NAME", "localhost:{0}".format(os.getenv("PORT", "8000"))
)
# SQLAlchemy.
pg_user = os.getenv("POSTGRES_USER", "neurone")
pg_pass = os.getenv("POSTGRES_PASSWORD", "password")
pg_host = os.getenv("POSTGRES_HOST", "neuronedb.postgres.database.azure.com")
pg_port = os.getenv("POSTGRES_PORT", "5432")
pg_db = os.getenv("POSTGRES_DB", 'postgres')
db = f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", db)

# Redis.
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Celery.
CELERY_CONFIG = {
    "broker_url": REDIS_URL,
    "result_backend": REDIS_URL,
    "include": [
        "neurone.blueprints.contact.tasks",
        "neurone.blueprints.user.tasks",
        "neurone.blueprints.billing.tasks",
    ],
    "beat_schedule": {
        "mark-soon-to-expire-credit-cards": {
            "task": "neurone.blueprints.billing.tasks.mark_old_credit_cards",
            "schedule": crontab(hour=0, minute=0),
        },
        "expire-old-coupons": {
            "task": "neurone.blueprints.billing.tasks.expire_old_coupons",
            "schedule": crontab(hour=0, minute=1),
        },
    },
}

# Flask-Mail.
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = os.getenv("MAIL_PORT", 587)
MAIL_USE_TLS = bool(strtobool(os.getenv("MAIL_USE_TLS", "true")))
MAIL_USE_SSL = bool(strtobool(os.getenv("MAIL_USE_SSL", "false")))
MAIL_USERNAME = os.getenv("MAIL_USERNAME", None)
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", None)
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "contact@local.host")

# Flask-Babel.
LANGUAGES = {"en": "English", "it": "Italian"}
BABEL_DEFAULT_LOCALE = "en"

# User.
SEED_ADMIN_USERNAME = os.getenv("SEED_ADMIN_USERNAME", "administrator")
SEED_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "dev@local.host")
SEED_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "password")
REMEMBER_COOKIE_DURATION = timedelta(days=90)

# Billing.
STRIPE_PUBLISHABLE_KEY = os.environ["STRIPE_PUBLISHABLE_KEY"]
STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]
STRIPE_API_VERSION = "2022-08-01"
STRIPE_CURRENCY = "eur"
STRIPE_TRIAL_PERIOD_DAYS = 0
STRIPE_PLANS = {
    "1": {
        "id": "gold",
        "name": "Gold",
        "amount": 300000,
        "currency": STRIPE_CURRENCY,
        "interval": "month",
        "interval_count": 1,
        "statement_descriptor": "NEURONE GOLD",
        "metadata": {"credits": 10, "recommended": True},
    },
    "2": {
        "id": "platinum",
        "name": "Platinum",
        "amount": 500000,
        "currency": STRIPE_CURRENCY,
        "interval": "month",
        "interval_count": 1,
        "statement_descriptor": "NEURONE PLATINUM",
        "metadata": {"credits": 20},
    },
}

CREDIT_BUNDLES = [
    {"credits": 1, "price_in_cents": 50000, "label": "Single valuation for €500"},
    {"credits": 10, "price_in_cents": 450000, "label": "10 valuations for €4500"},
    {"credits": 20, "price_in_cents": 800000, "label": "20 valuations for €8000"},
]


# Rate limiting.
RATELIMIT_STORAGE_URI = REDIS_URL
RATELIMIT_STRATEGY = "fixed-window-elastic-expiry"
RATELIMIT_HEADERS_ENABLED = True

# Google Analytics.
ANALYTICS_GOOGLE_UA = os.getenv("ANALYTICS_GOOGLE_UA", None)

# To create a webhook
'''
curl https://api.stripe.com/v1/webhook_endpoints \
  -u "sk_test_51PNwuML89Edeu0jAhy7KsiJcnqYuJRelwlbLkAfGi4TBlyG2VJECsvJ0GkpMsAMf2HGW7zGxUz67CiijxtHnGLTN00i3PyqDHj:" \
  -d "enabled_events[]"="invoice.created" \
  -d "api_version"="2022-08-01" \
  --data-urlencode url="https://7abd-93-68-152-180.ngrok-free.app/stripe_webhook/event"
'''
