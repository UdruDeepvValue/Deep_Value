from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms import SelectField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional

from config.settings import CREDIT_BUNDLES


def choices_from_credit_bundles():
    """
    Convert the credit_BUNDLE settings into select box items.

    :return: list
    """
    choices = []

    for bundle in CREDIT_BUNDLES:
        pair = (str(bundle.get("credits")), bundle.get("label"))
        choices.append(pair)

    return choices


class SubscriptionForm(FlaskForm):
    stripe_key = HiddenField(
        "Stripe publishable key", [DataRequired(), Length(1, 254)]
    )
    plan = HiddenField("Plan", [DataRequired(), Length(1, 254)])
    coupon_code = StringField(
        "Do you have a coupon code?", [Optional(), Length(1, 128)]
    )
    Companyname = StringField("Company Name", [DataRequired(), Length(1, 254)])
    Address = StringField("Address", [DataRequired(), Length(1, 254)])
    City = StringField("City", [DataRequired(), Length(1, 64)])
    State = StringField("State or Province", [DataRequired(), Length(1, 4)])
    Zip = StringField("Zip code", [DataRequired(), Length(1, 16)])
    Country = StringField("Country", [DataRequired(), Length(1, 254)])
    Vat = StringField("Vat Number", [DataRequired(), Length(1, 64)])
    Sdi = StringField("SDI", [Length(1, 64)])
    name = StringField("Cardholder's Name", [DataRequired(), Length(1, 254)])
    #Surname_card = StringField("Cardholder's Surname", [DataRequired(), Length(1, 254)])

class UpdateSubscriptionForm(FlaskForm):
    coupon_code = StringField(
        "Do you have a coupon code?", [Optional(), Length(1, 254)]
    )


class CancelSubscriptionForm(FlaskForm):
    pass


class PaymentForm(FlaskForm):
    stripe_key = HiddenField(
        "Stripe publishable key", [DataRequired(), Length(1, 254)]
    )
    credit_bundles = SelectField(
        "How many credits do you want?",
        [DataRequired()],
        choices=choices_from_credit_bundles(),
    )
    coupon_code = StringField(
        "Do you have a coupon code?", [Optional(), Length(1, 128)]
    )
    Companyname = StringField("Company Name", [DataRequired(), Length(1, 254)])
    Address = StringField("Address", [DataRequired(), Length(1, 254)])
    City = StringField("City", [DataRequired(), Length(1, 64)])
    State = StringField("State or Province", [DataRequired(), Length(1, 4)])
    Zip = StringField("Zip code", [DataRequired(), Length(1, 16)])
    Country = StringField("Country", [DataRequired(), Length(1, 254)])
    Vat = StringField("Vat Number", [DataRequired(), Length(1, 64)])
    Sdi = StringField("SDI", [Length(1, 64)])
    name = StringField("Cardholder's Name", [DataRequired(), Length(1, 254)])
    # Surname_card = StringField("Cardholder's Surname", [DataRequired(), Length(1, 254)])
