from neurone.blueprints.page.forms import Loginbutt, Signupbutt

from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for

page = Blueprint("page", __name__, template_folder="templates")
search = Blueprint("search", __name__, template_folder="templates")

@page.route('/', methods=['GET', 'POST'])
def home():
    logbut = Loginbutt()
    sigbut = Signupbutt()
    if logbut.validate_on_submit():
        return redirect(url_for('page.login'))
    if sigbut.validate_on_submit():
        return redirect(url_for('page.register'))
    '''msg = Message("Hello",
                  sender="info@deep-value.cloud",
                  recipients=["marco.colonna@zoho.eu"])
                  msg.body = "This is the email body"
    mail.send(msg)'''
    return render_template('page/home.html', form1=logbut, form2=sigbut)



@page.route('/privacy')
def privacy():
    return render_template('page/privacy.html')


@page.route('/cookies')
def cookies():
    return render_template('page/cookies.html')


@page.route('/terms')
def terms():
    return render_template('page/terms.html')
