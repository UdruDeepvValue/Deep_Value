from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    IntegerField,
    RadioField,
    BooleanField,
    FloatField
)
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from wtforms.validators import NumberRange
from neurone.blueprints.search.models.search import coutry_query, industry_query


class NeuroneForm(FlaskForm):
    pjn = StringField('Provide a confidential name to this search')
    Rev0 = IntegerField('Last Year Revenue in thousands',
                        validators=[DataRequired()])
    Ebitda = IntegerField('Last Year EBITDA in thousands',
                          validators=[DataRequired()])
    Fcff = IntegerField('Last Year FCFF in thousands',
                        validators=[DataRequired()])
    Rev1 = IntegerField('Previous Year Revenue in thousands',
                        validators=[DataRequired()])
    Hcagr = FloatField('3-5 Years Historical CAGR without %',
                       validators=[DataRequired()])
    Fcagr = FloatField('3-5 Years Forecasted CAGR without %',
                       validators=[DataRequired()])
    Arr = IntegerField('percentage of recurring revenue (ARR) without %',
                       validators=[DataRequired()])
    Country = QuerySelectField(query_factory=coutry_query, allow_blank=True,
                               get_label='country',
                               validators=[DataRequired()])
    Industry = QuerySelectField(query_factory=industry_query, allow_blank=True,
                                get_label='industry',
                                validators=[DataRequired()])
    Listed = RadioField('The Company is Listed?',
                        choices=[(1, 'yes'), (0, 'No')],
                        validators=[DataRequired()])
                        #render_kw={'class': 'no_bullets'})
    gdpr = BooleanField('<b>GDPR acknowledgement:</b> I agree that this site '
                        'stores the information I submit so that '
                        'they can respond to my requests.',
                        validators=[DataRequired()])
    submit = SubmitField('Deep Value it')
