import logging
from logging.handlers import SMTPHandler

import stripe
from celery import Celery
from celery import Task
from flask import Flask
from flask import render_template
from flask import request
from flask_login import current_user
from werkzeug.debug import DebuggedApplication
from werkzeug.middleware.proxy_fix import ProxyFix

from cli import register_cli_commands
from config.settings import LANGUAGES
from neurone.blueprints.admin.views import admin
from neurone.blueprints.search.views import search
from neurone.blueprints.billing.template_processors import current_year
from neurone.blueprints.billing.template_processors import format_currency
from neurone.blueprints.billing.views.billing import billing
from neurone.blueprints.billing.views.stripe_webhook import stripe_webhook
from neurone.blueprints.contact.views import contact
from neurone.blueprints.page.views import page
from neurone.blueprints.up.views import up
from neurone.blueprints.user.models import User
from neurone.blueprints.user.views import user
from neurone.extensions import babel
from neurone.extensions import csrf
from neurone.extensions import db
from neurone.extensions import debug_toolbar
from neurone.extensions import flask_static_digest
from neurone.extensions import limiter
from neurone.extensions import login_manager
from neurone.extensions import mail
from neurone.extensions import bootstrap


def create_celery_app(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery = Celery(app.import_name, task_cls=FlaskTask)
    celery.conf.update(app.config.get("CELERY_CONFIG", {}))
    celery.set_default()
    app.extensions["celery"] = celery

    return celery


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, static_folder="../public", static_url_path="")

    app.config.from_object("config.settings")

    if settings_override:
        app.config.update(settings_override)

    stripe.api_key = app.config.get("STRIPE_SECRET_KEY")
    stripe.api_version = app.config.get("STRIPE_API_VERSION")

    middleware(app)
    error_templates(app)
    exception_handler(app)
    app.register_blueprint(up)
    app.register_blueprint(admin)
    app.register_blueprint(page)
    app.register_blueprint(contact)
    app.register_blueprint(user)
    app.register_blueprint(billing)
    app.register_blueprint(stripe_webhook)
    app.register_blueprint(search)
    template_processors(app)
    extensions(app)
    authentication(app, User)
    register_cli_commands(app)

    return app


def get_locale():
    """
    Initialize a locale for the current request.

    :return: str
    """
    if current_user.is_authenticated:
        return current_user.locale

    accept_languages = LANGUAGES.keys()
    return request.accept_languages.best_match(accept_languages)


def extensions(app):
    """
    Register 0 or more extensions (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    debug_toolbar.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    limiter.init_app(app)
    # babel.init_app(app, locale_selector=get_locale)
    flask_static_digest.init_app(app)

    return None


def template_processors(app):
    """
    Register 0 or more custom template processors (mutates the app passed in).

    :param app: Flask application instance
    :return: App jinja environment
    """
    app.jinja_env.filters["format_currency"] = format_currency
    app.jinja_env.globals.update(current_year=current_year)

    return app.jinja_env


def authentication(app, user_model):
    """
    Initialize the Flask-Login extension (mutates the app passed in).

    :param app: Flask application instance
    :param user_model: Model that contains the authentication information
    :type user_model: SQLAlchemy model
    :return: None
    """
    login_manager.login_view = "user.login"

    @login_manager.user_loader
    def load_user(uid):
        user = user_model.query.get(uid)

        if not user.is_active():
            login_manager.login_message_category = "error"
            login_manager.login_message = "This account has been disabled."

            return None

        return user


def middleware(app):
    """
    Register 0 or more middleware (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    # Enable the Flask interactive debugger in the brower for development.
    if app.debug:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    # Set the real IP address into request.remote_addr when behind a proxy.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    return None


def error_templates(app):
    """
    Register 0 or more custom error pages (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    def render_status(status):
        """
        Render a custom template for a specific status.
          Source: http://stackoverflow.com/a/30108946

        :param status: Status as a written name
        :type status: str
        :return: None
        """
        # Get the status code from the status, default to a 500 so that we
        # catch all types of errors and treat them as a 500.
        code = getattr(status, "code", 500)
        return render_template("errors/{0}.html".format(code)), code

    for error in [404, 429, 500]:
        app.errorhandler(error)(render_status)

    return None


def exception_handler(app):
    """
    Register 0 or more exception handlers (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """
    mail_handler = SMTPHandler(
        (app.config.get("MAIL_SERVER"), app.config.get("MAIL_PORT")),
        app.config.get("MAIL_USERNAME"),
        [app.config.get("MAIL_USERNAME")],
        "[Exception handler] A 5xx was thrown",
        (app.config.get("MAIL_USERNAME"), app.config.get("MAIL_PASSWORD")),
        secure=(),
    )

    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(
        logging.Formatter(
            """
    Time:               %(asctime)s
    Message type:       %(levelname)s


    Message:

    %(message)s
    """
        )
    )
    app.logger.addHandler(mail_handler)

    return None


celery_app = create_celery_app()
