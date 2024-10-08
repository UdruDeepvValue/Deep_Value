from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from sqlalchemy import text

from neurone.blueprints.admin.forms import BulkDeleteForm
from neurone.blueprints.admin.forms import CouponForm
from neurone.blueprints.admin.forms import SearchForm
from neurone.blueprints.admin.forms import UserCancelSubscriptionForm
from neurone.blueprints.admin.forms import UserForm
from neurone.blueprints.admin.models import Dashboard
from neurone.blueprints.billing.decorators import handle_stripe_exceptions
from neurone.blueprints.billing.models.coupon import Coupon
from neurone.blueprints.billing.models.invoice import Invoice
from neurone.blueprints.billing.models.subscription import Subscription
from neurone.blueprints.user.decorators import role_required
from neurone.blueprints.user.models import User

admin = Blueprint(
    "admin", __name__, template_folder="templates", url_prefix="/admin"
)


@admin.before_request
@login_required
@role_required("admin")
def before_request():
    """Protect all of the admin endpoints."""
    pass


# Dashboard -------------------------------------------------------------------
@admin.route('')
def dashboard():
    group_and_count_plans = Dashboard.group_and_count_plans()
    group_and_count_coupons = Dashboard.group_and_count_coupons()
    group_and_count_users = Dashboard.group_and_count_users()
    # group_and_count_payouts = Dashboard.group_and_count_payouts()

    return render_template(
        "admin/page/dashboard.html",
        group_and_count_plans=group_and_count_plans,
        group_and_count_coupons=group_and_count_coupons,
        group_and_count_users=group_and_count_users,
        # group_and_count_payouts=group_and_count_payouts,
    )


# Users -----------------------------------------------------------------------
@admin.get("/users", defaults={"page": 1})
@admin.get("/users/page/<int:page>")
def users(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = User.sort_by(
        request.args.get("sort", "created_on"),
        request.args.get("direction", "desc"),
    )
    order_values = "{0} {1}".format(sort_by[0], sort_by[1])

    paginated_users = (
        User.query.filter(User.search(request.args.get("q", text(""))))
        .order_by(User.roles.asc(), User.payment_id, text(order_values))
        .paginate(page=page, per_page=50)
    )

    return render_template(
        "admin/user/index.html",
        form=search_form,
        bulk_form=bulk_form,
        users=paginated_users,
    )


@admin.route("/users/edit/<int:id>", methods=["GET", "POST"])
def users_edit(id):
    user = User.query.get(id)
    form = UserForm(obj=user)

    if current_user.subscription:
        coupon = Coupon.query.filter(
            Coupon.code == current_user.subscription.coupon
        ).first()
    else:
        coupon = None

    if form.validate_on_submit():
        if User.is_last_admin(
            user, request.form.get("role"), request.form.get("active")
        ):
            flash("You are the last admin, you cannot do that.", "error")
            return redirect(url_for("admin.users"))

        form.populate_obj(user)

        user.save()

        flash("User has been saved successfully.", "success")
        return redirect(url_for("admin.users"))

    return render_template(
        "admin/user/edit.html", form=form, user=user, coupon=coupon
    )


@admin.post("/users/bulk_delete")
def users_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = User.get_bulk_action_ids(
            request.form.get("scope"),
            request.form.getlist("bulk_ids"),
            omit_ids=[current_user.id],
            query=request.args.get("q", text("")),
        )

        # Prevent circular imports.
        from neurone.blueprints.billing.tasks import delete_users

        delete_users.delay(ids)

        flash(
            "{0} user(s) were scheduled to be deleted.".format(len(ids)),
            "success",
        )
    else:
        flash("No users were deleted, something went wrong.", "error")

    return redirect(url_for("admin.users"))


@admin.post("/users/cancel_subscription")
def users_cancel_subscription():
    form = UserCancelSubscriptionForm()

    if form.validate_on_submit():
        user = User.query.get(request.form.get("id"))

        if user:
            subscription = Subscription()
            if subscription.cancel(user):
                flash(
                    "Subscription has been cancelled for {0}.".format(
                        user.name
                    ),
                    "success",
                )
        else:
            flash(
                "No subscription was cancelled, something went wrong.", "error"
            )

    return redirect(url_for("admin.users"))


# Coupons ---------------------------------------------------------------------
@admin.get("/coupons", defaults={"page": 1})
@admin.get("/coupons/page/<int:page>")
def coupons(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = Coupon.sort_by(
        request.args.get("sort", "created_on"),
        request.args.get("direction", "desc"),
    )
    order_values = "{0} {1}".format(sort_by[0], sort_by[1])

    paginated_coupons = (
        Coupon.query.filter(Coupon.search(request.args.get("q", text(""))))
        .order_by(text(order_values))
        .paginate(page=page, per_page=50)
    )

    return render_template(
        "admin/coupon/index.html",
        form=search_form,
        bulk_form=bulk_form,
        coupons=paginated_coupons,
    )


@admin.route("/coupons/new", methods=["GET", "POST"])
@handle_stripe_exceptions
def coupons_new():
    coupon = Coupon()
    form = CouponForm(obj=coupon)

    if form.validate_on_submit():
        form.populate_obj(coupon)

        params = {
            "code": coupon.code,
            "duration": coupon.duration,
            "percent_off": coupon.percent_off,
            "amount_off": coupon.amount_off,
            "currency": coupon.currency,
            "redeem_by": coupon.redeem_by,
            "max_redemptions": coupon.max_redemptions,
            "duration_in_months": coupon.duration_in_months,
        }

        if Coupon.create(params):
            flash("Coupon has been created successfully.", "success")
            return redirect(url_for("admin.coupons"))

    return render_template("admin/coupon/new.html", form=form, coupon=coupon)


@admin.post("/coupons/bulk_delete")
def coupons_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = Coupon.get_bulk_action_ids(
            request.form.get("scope"),
            request.form.getlist("bulk_ids"),
            query=request.args.get("q", text("")),
        )

        # Prevent circular imports.
        from neurone.blueprints.billing.tasks import delete_coupons

        delete_coupons.delay(ids)

        flash(
            "{0} coupons(s) were scheduled to be deleted.".format(len(ids)),
            "success",
        )
    else:
        flash("No coupons were deleted, something went wrong.", "error")

    return redirect(url_for("admin.coupons"))


# Invoices --------------------------------------------------------------------
@admin.get("/invoices", defaults={"page": 1})
@admin.get("/invoices/page/<int:page>")
def invoices(page):
    search_form = SearchForm()

    sort_by = Invoice.sort_by(
        request.args.get("sort", "created_on"),
        request.args.get("direction", "desc"),
    )
    order_values = "invoices.{0} {1}".format(sort_by[0], sort_by[1])

    paginated_invoices = (
        Invoice.query.join(User)
        .filter(Invoice.search(request.args.get("q", text(""))))
        .order_by(text(order_values))
        .paginate(page=page, per_page=50)
    )

    return render_template(
        "admin/invoice/index.html",
        form=search_form,
        invoices=paginated_invoices,
    )
