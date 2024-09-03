from lib.flask_mailplus import send_template_message
from neurone.app import create_celery_app
from neurone.blueprints.user.models import User
from flask import current_app

celery = create_celery_app()


@celery.task()
def deliver_new_user_email(user_id):
    """
    Send a contact e-mail.

    :param email: E-mail address of the visitor
    :type user_id: str
    :param message: E-mail message
    :type user_id: str
    :return: None
    """
    user = User.query.get(user_id)

    if user is None:
        return
    ctx = {"user": user}

    send_template_message(
        subject="New Active User",
        # sender=[current_app.config["MAIL_DEFAULT_SENDER"]],
        recipients=[current_app.config["MAIL_DEFAULT_SENDER"]],
        # reply_to=email,
        template="user/mail/user_registered",
        ctx=ctx,
    )

    return None


@celery.task()
def deliver_identity_conf_email(user_id, reset_token):
    """
    Send a reset password e-mail to a user.

    :param user_id: The user id
    :type user_id: int
    :param reset_token: The reset token
    :type reset_token: str
    :return: None if a user was not found
    """
    user = User.query.get(user_id)

    if user is None:
        return

    ctx = {'user': user, 'reset_token': reset_token}

    send_template_message(subject='Confirm email from Deep Value',
                          recipients=[user.email],
                          template='user/mail/email_confirm',
                          ctx=ctx)

    return None


@celery.task()
def deliver_password_reset_email(user_id, reset_token):
    """
    Send a reset password e-mail to a user.

    :param user_id: The user id
    :type user_id: int
    :param reset_token: The reset token
    :type reset_token: str
    :return: None if a user was not found
    """
    user = User.query.get(user_id)

    if user is None:
        return

    ctx = {"user": user, "reset_token": reset_token}

    send_template_message(
        subject="Password reset from Deep Value",
        recipients=[user.email],
        template="user/mail/password_reset",
        ctx=ctx,
    )

    return None
