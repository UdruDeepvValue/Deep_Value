from functools import wraps

from flask import flash
from flask import redirect
from flask import url_for
from flask_login import current_user


def credits_required(f):
    """
    Restrict access from users who have no credits.

    :return: Function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.credits == 0:
            flash(
                "Sorry, you're out of credits. You should buy more.", "warning"
            )
            return redirect(url_for("billing.pricing"))

        return f(*args, **kwargs)

    return decorated_function
