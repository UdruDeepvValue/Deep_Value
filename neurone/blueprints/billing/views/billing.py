from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_babel import gettext as _
from flask_login import current_user
from flask_login import login_required

from config import settings
from lib.util_json import render_json
from neurone.blueprints.billing.decorators import handle_stripe_exceptions
from neurone.blueprints.billing.decorators import subscription_required
from neurone.blueprints.billing.forms import CancelSubscriptionForm
from neurone.blueprints.billing.forms import PaymentForm
from neurone.blueprints.billing.forms import SubscriptionForm
from neurone.blueprints.billing.forms import UpdateSubscriptionForm
from neurone.blueprints.billing.models.coupon import Coupon
from neurone.blueprints.billing.models.invoice import Invoice, Purchase
from neurone.blueprints.billing.models.subscription import Subscription
from neurone.blueprints.user.models import db

billing = Blueprint(
    "billing",
    __name__,
    template_folder="../templates",
    url_prefix="/subscription",
)


@billing.get("/pricing")
def pricing():
    if current_user.is_authenticated and current_user.subscription:
        return redirect(url_for("billing.update"))

    form = UpdateSubscriptionForm()

    return render_template(
        "billing/pricing.html", form=form, plans=settings.STRIPE_PLANS
    )


@billing.post("/coupon_code")
@login_required
def coupon_code():
    code = request.form.get("coupon_code")

    if code is None:
        return render_json(422, {"error": "Coupon code cannot be processed."})

    coupon = Coupon.find_by_code(code)
    if coupon is None:
        return render_json(404, {"error": "Coupon code not found."})

    return render_json(200, {"data": coupon.to_json()})


@billing.route("/create", methods=["GET", "POST"])
@handle_stripe_exceptions
@login_required
def create():
    if current_user.subscription:
        flash("You already have an active subscription.", "info")
        return redirect(url_for("user.profile"))

    plan = request.args.get("plan")
    subscription_plan = Subscription.get_plan_by_id(plan)

    # Guard against an invalid or missing plan.
    if subscription_plan is None and request.method == "GET":
        flash("Sorry, that plan did not exist.", "error")
        return redirect(url_for("billing.pricing"))

    stripe_key = current_app.config.get("STRIPE_PUBLISHABLE_KEY")
    form = SubscriptionForm(stripe_key=stripe_key, plan=plan)

    if form.validate_on_submit():
        #invoice = Invoice()
        subscription = Subscription()
        created = subscription.create(
            user=current_user,
            name=request.form.get("Companyname"),
            plan=request.form.get("plan"),
            coupon_code=request.form.get("coupon_code"),
            token=request.form.get("stripe_token"),
        )

        get_plan = current_app.config.get("STRIPE_PLANS")
        plan_form = request.form.get("plan")
        print(plan_form)
        plan_detail = next((plan for plan in get_plan.values() if plan["id"] == plan_form), None)
        print(plan_detail.get('amount'))
        print(type(plan_detail))

        '''created2 = invoice.create(
            user=current_user,
            currency=current_app.config.get("STRIPE_CURRENCY"),
            amount=request.form.get("plan"),
            #credits=credit_bundles_form,
            #coupon=request.form.get("coupon_code"),
            token=request.form.get("stripe_token"),
        )'''
        print('CREDITS OF THE PLAN: ', plan_detail.get('metadata').get('credits'))

        if created:
            purchase = Purchase(
                            user_id=current_user.id,
                            user=current_user,
                            company_name=request.form.get("Companyname"),
                            address=request.form.get("Address"),
                            city=request.form.get("City"),
                            state=request.form.get("State"),
                            zip=request.form.get("Zip"),
                            country=request.form.get("Country"),
                            vat_n=request.form.get("Vat"),
                            sdi=request.form.get("Sdi"),
                            name_card=request.form.get("name"),
                            #surname_card=request.form.get("Surname_card"),
                            product="Subscription " + request.form.get("plan"),                            description=request.form.get("plan"),
                            #period_start_on="",
                            #period_end_on="",
                            currency="EUR",
                            #tax="",
                            #tax_percent="",
                            total=plan_detail.get("amount")/100,
                            #cc_brand=current_user.credit_card.brand,
                            #last4=current_user.credit_card.last4,
                            #exp_date=current_user.credit_card.exp_date
                        )
            user = current_user
            user.credits += plan_detail.get('metadata').get('credits')
            db.session.add(purchase)
            db.session.add(user)
            db.session.commit()
            flash("Awesome, thanks for subscribing!", "success")
        else:
            flash("You must enable JavaScript for this request.", "warning")


        return redirect(url_for("user.profile"))

    return render_template(
        "billing/payment_method.html", form=form, plan=subscription_plan
    )


@billing.route("/update", methods=["GET", "POST"])
@handle_stripe_exceptions
@login_required
@subscription_required
def update():
    current_plan = current_user.subscription.plan
    active_plan = Subscription.get_plan_by_id(current_plan)
    new_plan = Subscription.get_new_plan(request.form.keys())

    plan = Subscription.get_plan_by_id(new_plan)

    # Guard against an invalid, missing or identical plan.
    is_same_plan = new_plan == active_plan["id"]
    if (
        (new_plan is not None and plan is None) or is_same_plan
    ) and request.method == "POST":
        return redirect(url_for("billing.update"))

    form = UpdateSubscriptionForm(coupon_code=current_user.subscription.coupon)

    if form.validate_on_submit():
        subscription = Subscription()
        updated = subscription.update(
            user=current_user,
            coupon_code=request.form.get("coupon_code"),
            plan=plan.get("id"),
        )

        if updated:
            flash("Your subscription has been updated.", "success")
            return redirect(url_for("user.profile"))
        else:
            flash("That coupon code is not valid.", "error")
            return redirect(url_for("billing.update"))

    return render_template(
        "billing/pricing.html",
        form=form,
        plans=settings.STRIPE_PLANS,
        active_plan=active_plan,
    )


@billing.route("/cancel", methods=["GET", "POST"])
@handle_stripe_exceptions
@login_required
def cancel():
    if not current_user.subscription:
        flash("You do not have an active subscription.", "error")
        return redirect(url_for("user.profile"))

    form = CancelSubscriptionForm()

    if form.validate_on_submit():
        subscription = Subscription()
        cancelled = subscription.cancel(user=current_user)

        if cancelled:
            flash("Sorry to see you go, your subscription has been "
                    "cancelled.", "success",)
            return redirect(url_for("user.profile"))

    return render_template("billing/cancel.html", form=form)


@billing.route("/update_payment_method", methods=["GET", "POST"])
@handle_stripe_exceptions
@login_required
def update_payment_method():
    if not current_user.credit_card:
        flash("You do not have a payment method on file.", "error")
        return redirect(url_for("user.profile"))

    active_plan = Subscription.get_plan_by_id(current_user.subscription.plan)

    card = current_user.credit_card
    stripe_key = current_app.config.get("STRIPE_PUBLISHABLE_KEY")
    form = SubscriptionForm(
        stripe_key=stripe_key, plan=active_plan, name=current_user.name
    )

    if form.validate_on_submit():
        subscription = Subscription()
        updated = subscription.update_payment_method(
            user=current_user,
            credit_card=card,
            name=request.form.get("name"),
            token=request.form.get("stripe_token"),
        )

        if updated:
            flash("Your payment method has been updated.", "success")
        else:
            flash("You must enable JavaScript for this request.", "warning")

        return redirect(url_for("user.profile"))

    return render_template(
        "billing/payment_method.html",
        form=form,
        plan=active_plan,
        card_last4=card.last4,
    )


@billing.get("/billing_details", defaults={"page": 1})
@billing.get("/billing_details/page/<int:page>")
@handle_stripe_exceptions
@login_required
def billing_details(page):
    paginated_invoices = (
        Invoice.query.filter(Invoice.user_id == current_user.id)
        .order_by(Invoice.created_on.desc())
        .paginate(page=page, per_page=12)
    )

    if current_user.subscription:
        upcoming = Invoice.upcoming(current_user.payment_id)
        coupon = Coupon.query.filter(
            Coupon.code == current_user.subscription.coupon
        ).first()
    else:
        upcoming = None
        coupon = None

    return render_template(
        "billing/billing_details.html",
        paginated_invoices=paginated_invoices,
        upcoming=upcoming,
        coupon=coupon,
    )


@billing.route("/purchase_credits", methods=["GET", "POST"])
@login_required
def purchase_credits():
    stripe_key = current_app.config.get("STRIPE_PUBLISHABLE_KEY")
    form = PaymentForm(stripe_key=stripe_key)

    if form.validate_on_submit():
        credit_bundles = current_app.config.get("CREDIT_BUNDLES")
        credit_bundles_form = int(request.form.get("credit_bundles"))

        bundle = next((item for item in credit_bundles if
                 item["credits"] == credit_bundles_form), None,
        )

        if bundle is not None:
            invoice = Invoice()
            created = invoice.create(
                user=current_user,
                currency=current_app.config.get("STRIPE_CURRENCY"),
                amount=bundle.get("price_in_cents"),
                credits=credit_bundles_form,
                coupon=request.form.get("coupon_code"),
                token=request.form.get("stripe_token"),
            )

            if created:
                purchase = Purchase(
                            user_id=current_user.id,
                            user=current_user,
                            company_name=request.form.get("Companyname"),
                            address=request.form.get("Address"),
                            city=request.form.get("City"),
                            state=request.form.get("State"),
                            zip=request.form.get("Zip"),
                            country=request.form.get("Country"),
                            vat_n=request.form.get("Vat"),
                            sdi=request.form.get("Sdi"),
                            name_card=request.form.get("name"),
                            #surname_card=request.form.get("Surname_card"),
                            product="Single/Bundle " + str(request.form.get("credit_bundles")),
                            description=str(request.form.get("credit_bundles")),
                            #period_start_on="",
                            #period_end_on="",
                            currency="EUR",
                            #tax="",
                            #tax_percent="",
                            total=bundle.get("price_in_cents")/100
                            #cc_brand=current_user.credit_card.brand,
                            #last4=current_user.credit_card.last4,
                            #exp_date=current_user.credit_card.exp_date
                        )
                #user = current_user
                #user.credits += credit_bundles_form
                db.session.add(purchase)
                #db.session.add(user)
                db.session.commit()
                flash("{} credits have been added to your account".format(credit_bundles_form), "success")

            else:
                flash("You must enable JavaScript for this request.", "warning",)

            return redirect(url_for("search.neurone"))

    return render_template("billing/purchase_credits.html", form=form)
