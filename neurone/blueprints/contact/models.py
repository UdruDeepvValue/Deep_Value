from neurone.extensions import db


class Messages(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(60))
    message = db.Column(db.Text)
    sent_on = db.Column(db.DateTime)
