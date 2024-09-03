from lib.util_datetime import tzware_datetime
from lib.util_sqlalchemy import ResourceMixin
from neurone.extensions import db
from flask_login import current_user
from flask_login import UserMixin
from sqlalchemy import text
from sqlalchemy import or_

class Neurone_entries(ResourceMixin, db.Model):
    __tablename__ = 'neurone_entries'
    id = db.Column(db.Integer, primary_key=True)

    # Relationships.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)

    # Search details.
    pj_name = db.Column(db.String(120))
    email = db.Column(db.String(30))
    rev0 = db.Column(db.Integer)
    ebitda = db.Column(db.Integer)
    fcff = db.Column(db.Integer)
    rev1 = db.Column(db.Integer)
    hcagr = db.Column(db.Float)
    fcagr = db.Column(db.Float)
    arr = db.Column(db.Integer)
    country = db.Column(db.String(50))
    industry = db.Column(db.String(50))
    listed = db.Column(db.Integer)
    entry_date = db.Column(db.DateTime)
    key = db.Column(db.String(255))

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Neurone_entries, self).__init__(**kwargs)


    def save_and_update_user(self, user):
        """
        Commit the search and update the user's information.

        :return: SQLAlchemy save result
        """
        self.save()

        user.credits += -1
        user.last_search_on = tzware_datetime()
        return user.save()

class NeuroneDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Relationships.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                  onupdate='CASCADE',
                                                  ondelete='CASCADE'),
                        index=True, nullable=False)

    # Search details.
    low = db.Column(db.Float)
    high = db.Column(db.Float)
    EV_EBITDA = db.Column(db.Float)
    ebitda_perc = db.Column(db.Float)
    growth = db.Column(db.Float)
    small = db.Column(db.Float)
    medium = db.Column(db.Float)
    big = db.Column(db.Float)
    market_EV = db.Column(db.Float)
    SP_yield = db.Column(db.Float)
    cash_ebitda = db.Column(db.Float)
    rule40 = db.Column(db.Float)
    itsSW = db.Column(db.Integer)
    itsListed = db.Column(db.Float)
    country_rank = db.Column(db.Float)
    submit_date = db.Column(db.DateTime)
    pj_name = db.Column(db.String(120))
    key = db.Column(db.String(255))
    email = db.Column(db.String(30))
    report1 = db.Column(db.Text)
    report2 = db.Column(db.Text)

    def __repr__(self):
        return '[Industries {}]'.format(self.industry)

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if query == "":
            return text("")
        from neurone.blueprints.user.models import User
        search_query = "%{0}%".format(query)
        search_chain = (
            User.email.ilike(current_user.email),
            NeuroneDB.pj_name.ilike(search_query),
            NeuroneDB.key.ilike(search_query),
        )

        return or_(*search_chain)

def industry_query():
    return Industries.query


class Countries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(255))
    rank = db.Column(db.Float)
    tax = db.Column(db.Float)

    def __repr__(self):
        return '[Countries {}]'.format(self.country)


def coutry_query():
    return Countries.query


class Industries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    industry = db.Column(db.String(255))
    multiple = db.Column(db.Float)