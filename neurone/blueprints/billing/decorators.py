from functools import wraps

import stripe
from flask import flash
from flask import redirect
from flask import url_for
from flask_login import current_user


def subscription_required(f):
    """
    Ensure a user is subscribed, if not redirect them to the pricing table.

    :return: Function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.subscription:
            return redirect(url_for("billing.pricing"))

        return f(*args, **kwargs)

    return decorated_function


def handle_stripe_exceptions(f):
    """
    Handle Stripe exceptions so they do not throw 500s.

    :param f:
    :type f: Function
    :return: Function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except stripe.error.CardError:
            flash("Sorry, your card was declined. Try again perhaps?", "error")
            return redirect(url_for("user.profile"))
        except stripe.error.InvalidRequestError as e:
            flash(str(e), "error")
            return redirect(url_for("user.profile"))
        except stripe.error.AuthenticationError:
            flash("Authentication with our payment gateway failed.", "error")
            return redirect(url_for("user.profile"))
        except stripe.error.APIConnectionError:
            flash(
                "Our payment gateway is experiencing connectivity issues"
                ", please try again.",
                "error",
            )
            return redirect(url_for("user.profile"))
        except stripe.error.StripeError:
            flash(
                "Our payment gateway is having issues, please try again.",
                "error",
            )
            return redirect(url_for("user.profile"))

    return decorated_function
