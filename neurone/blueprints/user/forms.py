from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms import StringField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms import BooleanField
from wtforms import SelectField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Email
from wtforms.validators import Optional
from wtforms.validators import EqualTo
from wtforms.validators import Regexp
from wtforms_alchemy.validators import Unique
# from wtforms_components import Email
# from wtforms_components import EmailField
from collections import OrderedDict

from config.settings import LANGUAGES
from lib.util_wtforms import ModelForm
from lib.util_wtforms import choices_from_dict
from neurone.blueprints.user.models import User
from neurone.blueprints.user.validations import (
    ensure_existing_password_matches,
)
from neurone.blueprints.user.validations import ensure_identity_exists


class SearchForm(FlaskForm):
    q = StringField("Search terms", [Optional(), Length(1, 256)])


class BulkDeleteForm(FlaskForm):
    SCOPE = OrderedDict(
        [
            ("all_selected_items", "All selected items"),
            ("all_search_results", "All search results"),
        ]
    )

    scope = SelectField(
        "Privileges",
        [DataRequired()],
        choices=choices_from_dict(SCOPE, prepend_blank=False),
    )


class LoginForm(FlaskForm):
    next = HiddenField()
    identity = StringField(
        "Email", [DataRequired(), Email(), Length(3, 254)]
    )
    password = PasswordField("Password", [DataRequired(), Length(5, 128)])
    remember_me = BooleanField('Stay signed in')
    submit = SubmitField('Login')


class BeginPasswordResetForm(FlaskForm):
    identity = StringField(
        "Your email",
        [DataRequired(), Length(3, 254), ensure_identity_exists, Email()],
    )
    submit = SubmitField('Submit')


class EmailConfForm(FlaskForm):
    reset_token = HiddenField()
    submit = SubmitField('Confirm Email')


class PasswordResetForm(FlaskForm):
    reset_token = HiddenField()
    password = PasswordField("Password", [DataRequired(), Length(5, 128)])
    submit = SubmitField('Submit')


class SignupForm(ModelForm):
    name = StringField('Your First Name', validators=[DataRequired()])
    surname = StringField('Your Family Name', validators=[DataRequired()])
    company = StringField('Company Name', validators=[DataRequired()])
    email = StringField('Your Email', validators=[DataRequired(), Email()])
    password = PasswordField('Your Password',
                             validators=[DataRequired(),
                                         Length(5, 128),
                                         EqualTo('confirm_password',
                                                 'Passwords do not match!')])
    confirm_password = PasswordField('Confirm Password')
    gdpr = BooleanField(
        '<b>GDPR acknowledgement:</b> I agree that this site stores the '
        'information I submit so that they can respond to my requests.',
        validators=[DataRequired()])
    submit = SubmitField('Sign up')


class UpdateCredentialsForm(ModelForm):
    current_password = PasswordField(
        "Current password",
        [DataRequired(), Length(5, 128), ensure_existing_password_matches],
    )

    email = StringField('New Email', validators=[Email(), Unique(User.email)])
    password = PasswordField("New Password", [Optional(), Length(5, 128)])
    submit = SubmitField('Update')


class UpdateLocaleForm(FlaskForm):
    locale = SelectField(
        "Language preference",
        [DataRequired()],
        choices=choices_from_dict(LANGUAGES, prepend_blank=False),
    )
