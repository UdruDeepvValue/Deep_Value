from flask import current_app

from lib.flask_mailplus import send_template_message
from neurone.app import create_celery_app

celery = create_celery_app()


@celery.task()
def deliver_contact_email(email, message):
    """
    Send a contact e-mail.

    :param email: E-mail address of the visitor
    :type user_id: str
    :param message: E-mail message
    :type user_id: str
    :return: None
    """
    ctx = {"email": email, "message": message}

    send_template_message(
        subject="Deep Value Contact",
        # sender=[current_app.config["MAIL_DEFAULT_SENDER"]],
        recipients=[current_app.config["MAIL_DEFAULT_SENDER"]],
        # reply_to=email,
        template="contact/mail/index",
        ctx=ctx,
    )

    return None
