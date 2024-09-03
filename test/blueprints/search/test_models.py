import datetime

import pytz

# from neurone.blueprints.search.models.search import Bet
from neurone.blueprints.search.models.credit import add_subscription_credits
# from neurone.blueprints.search.models.dice import roll
from neurone.blueprints.billing.models.subscription import Subscription


class Testcredit(object):
    def test_add_credits_to_subscription_upgrade(self):
        """Add credits to a subscription upgrade."""
        credits = 10

        current_plan = Subscription.get_plan_by_id("gold")
        new_plan = Subscription.get_plan_by_id("platinum")

        credits = add_subscription_credits(credits, current_plan, new_plan, None)

        assert credits == 20

    def test_no_credit_change_for_subscription_downgrade(self):
        """Same credits for a subscription downgrade."""
        credits = 10

        current_plan = Subscription.get_plan_by_id("platinum")
        new_plan = Subscription.get_plan_by_id("gold")

        credits = add_subscription_credits(credits, current_plan, new_plan, None)

        assert credits == 10

    def test_no_credit_change_for_same_subscription(self):
        """Same credits for the same subscription."""
        credits = 10

        current_plan = Subscription.get_plan_by_id("gold")
        new_plan = Subscription.get_plan_by_id("gold")

        may_29_2015 = datetime.datetime(2015, 5, 29, 0, 0, 0)
        may_29_2015 = pytz.utc.localize(may_29_2015)

        credits = add_subscription_credits(
            credits, current_plan, new_plan, may_29_2015
        )

        assert credits == 10

    # Add tests for Neurone
