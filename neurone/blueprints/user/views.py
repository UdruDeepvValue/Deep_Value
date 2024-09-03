from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from sqlalchemy import text

from datetime import datetime
from lib.security import safe_next_url
from neurone.blueprints.user.decorators import anonymous_required
from neurone.blueprints.user.forms import BeginPasswordResetForm
from neurone.blueprints.user.forms import LoginForm
from neurone.blueprints.user.forms import EmailConfForm
from neurone.blueprints.user.forms import PasswordResetForm
from neurone.blueprints.user.forms import SignupForm
from neurone.blueprints.user.forms import UpdateCredentialsForm
from neurone.blueprints.user.forms import UpdateLocaleForm
from neurone.blueprints.user.forms import BeginPasswordResetForm
from neurone.blueprints.user.models import User, db
from neurone.blueprints.search.models.search import NeuroneDB as Ndb
from neurone.blueprints.user.forms import SearchForm, BulkDeleteForm

user = Blueprint("user", __name__, template_folder="templates")
page = Blueprint('page', __name__, template_folder='templates')
search = Blueprint('search', __name__, template_folder='templates')


@user.route('/account/email_conf', methods=['GET', 'POST'])
@anonymous_required()
def email_conf():
    form = EmailConfForm(reset_token=request.args.get('reset_token'))

    if form.validate_on_submit():
        u = User.find_by_token(request.form.get("reset_token"))

        if u is None:
            flash('Your reset token has expired or was tampered with.',
                  'error')
            return redirect(url_for('user.login'))

        u.verified = 1
        db.session.commit()

        User.notify_new_user(u.email)

        if login_user(u):
            flash('your profile is now active.', 'success')
            return redirect(url_for('user.profile'))
    return render_template('user/email_conf.html', form=form)


@user.route("/login", methods=["GET", "POST"])
@anonymous_required()
def login():
    if current_user.is_authenticated:
        flash('you are already logged in!', "success")
        return redirect(url_for('search.neurone'))

    form = LoginForm()

    if form.validate_on_submit():
        u = User.find_by_identity(request.form.get("identity"))

        if not u.verified:
            flash('You need to verify your account. we have just sent you an email with the details.', "error")
            u.initialize_confirm_email(form.identity.data)
            return redirect(url_for('user.login'))

        if u is not None and u.check_password(form.password.data):
            u.update_activity_tracking(request.remote_addr)
            login_user(u, form.remember_me.data)
            return redirect(url_for('search.neurone'))
        else:
            flash('Invalid username or password')

    return render_template("user/login.html", form=form)


@user.get("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("page.home"))


@user.route("/account/begin_password_reset", methods=["GET", "POST"])
@anonymous_required()
def begin_password_reset():
    form = BeginPasswordResetForm()

    if form.validate_on_submit():
        u = User.initialize_password_reset(request.form.get("identity"))

        flash("An email has been sent to {0}.".format(u.email), "success")
        return redirect(url_for("user.login"))

    return render_template("user/begin_password_reset.html", form=form)


@user.route("/account/password_reset", methods=["GET", "POST"])
@anonymous_required()
def password_reset():
    form = PasswordResetForm(reset_token=request.args.get("reset_token"))

    if form.validate_on_submit():
        u = User.find_by_token(request.form.get("reset_token"))

        if u is None:
            flash(
                "Your reset token has expired or was tampered with.", "error"
            )
            return redirect(url_for("user.begin_password_reset"))

        form.populate_obj(u)
        u.password = form.password.data
        u.save()

        if login_user(u):
            flash("Your password has been reset.", "success")
            return redirect(url_for("user.profile"))

    return render_template("user/password_reset.html", form=form)


@user.route("/register", methods=["GET", "POST"])
@anonymous_required()
def register():
    form = SignupForm()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if form.validate_on_submit():
        user_check = User.query.filter_by(email=form.email.data).first()
        if user_check is None:
            user = User(name=form.name.data, surname=form.surname.data,
                        company=form.company.data, email=form.email.data,
                        password=form.password.data, join_date=now)
            db.session.add(user)
            db.session.commit()

            u = User.initialize_confirm_email(form.email.data)
            user.update_activity_tracking(request.remote_addr)

            flash('An email has been sent to {0}.'.format(u.email), 'success')

            return redirect(url_for('user.login'))
        else:
            flash('You are already registered! Login to access the page.')
            return redirect(url_for('user.login'))

    return render_template("user/register.html", form=form)



@user.get("/settings")
@login_required
def settings():
    return render_template("user/profile.html")


@user.route("/settings/update_credentials", methods=["GET", "POST"])
@login_required
def update_credentials():
    form = UpdateCredentialsForm(obj=current_user)
    email = current_user.email
    if form.validate_on_submit():
        u = User.query.filter_by(email=email).first()
        newemail = form.email.data
        old_password = form.current_password.data
        new_password = form.password.data
        if u.check_password(old_password):
            u.password = new_password
            u.email = newemail
            db.session.commit()
        flash("Your sign in settings have been updated.", "success")
        return redirect(url_for("user.profile"))
    else:
        flash('Wrong password!', "error")
        return render_template('user/update_credentials.html', form=form)

    return render_template("user/update_credentials.html", form=form)


@user.route("/settings/update_locale", methods=["GET", "POST"])
@login_required
def update_locale():
    form = UpdateLocaleForm(locale=current_user.locale)

    if form.validate_on_submit():
        form.populate_obj(current_user)
        current_user.save()

        flash("Your locale settings have been updated.", "success")
        return redirect(url_for("user.profile"))

    return render_template("user/update_locale.html", form=form)


@user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    email = current_user.email
    user = User.query.filter_by(email=email).first()
    userid = user.id
    cred = user.credits
    print(cred)
    name = user.name
    surname = user.surname
    join = user.created_on
    join = datetime.strftime(join, '%d %B %Y')

    dbu = (Ndb.query.filter_by(email=email).order_by
           (Ndb.submit_date.desc()).all())

    return render_template('user/profile.html',
                           email=email, name=name, cred=cred,
                           surname=surname, userid=str(userid),
                           join=join, title='Account', dbu=dbu)


#@user.route('/profile2')
@user.route('/profile2/page/<int:page>')
@login_required
def profile2(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()
    email = current_user.email
    u = User.query.filter_by(email=email).first()
    userid = u.id
    cred = u.credits
    name = u.name
    surname = u.surname
    join = u.join_date
    join = datetime.strftime(join, '%d %B %Y')

    dbu = (Ndb.query.filter_by(email=email).order_by
           (Ndb.submit_date.desc()).all())
    '''
    sort_by = Ndb.sort_by(
        request.args.get("sort", "created_on"),
        request.args.get("direction", "desc"),
    )'''
    # order_values = "{0} {1}".format(sort_by[0], sort_by[1])

    paginated_searches = (
        Ndb.query.join(User)
        .filter(Ndb.search(request.args.get("q", text(""))))
        .paginate(page=page, per_page=10)
    )

    return render_template(
        "user/profile2.html",
        form=search_form,
        bulk_form=bulk_form,
        users=paginated_searches,
        email=email, name=name, cred=cred,
        surname=surname, userid=str(userid),
        join=join, dbu=dbu,
    )