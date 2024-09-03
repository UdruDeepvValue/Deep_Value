from flask_wtf import FlaskForm
from wtforms import SubmitField


class Loginbutt(FlaskForm):
    submit = SubmitField('Login')


class Signupbutt(FlaskForm):
    submit = SubmitField('Signup')
