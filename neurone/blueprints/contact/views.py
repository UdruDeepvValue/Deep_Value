from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from datetime import datetime

from neurone.blueprints.contact.models import Messages, db
from neurone.blueprints.contact.forms import ContactForm

contact = Blueprint("contact", __name__, template_folder="templates")


@contact.route("/contact", methods=["GET", "POST"])
def index():
    # Pre-populate the email field if the user is signed in.
    form = ContactForm(obj=current_user)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if form.validate_on_submit():
        # This prevents circular imports.
        from neurone.blueprints.contact.tasks import deliver_contact_email

        deliver_contact_email.delay(
            request.form.get("email"), request.form.get("message")
        )
        message = Messages(email=form.email.data,
                           message=str(form.message.data),
                           sent_on=now)
        db.session.add(message)
        db.session.commit()

        flash("Thanks, expect a response shortly.", "success")
        return redirect(url_for("contact.index"))

    return render_template("contact/index.html", form=form)
