def add_subscription_credits(credits, previous_plan, plan, cancelled_on):
    """
    Add an amount of credits to an existing credit value.

    :param credits: Existing credit value
    :type credits: int
    :param previous_plan: Previous subscription plan
    :type previous_plan: dict
    :param plan: New subscription plan
    :type plan: dict
    :param cancelled_on: When a plan has potentially been cancelled
    :type cancelled_on: datetime
    :return: int
    """
    # Some people will try to game the system and cheat us for extra credits.
    #
    # Users should only be able to gain credits via subscription when:
    #   Subscribes for the first time
    #   Subscriber updates to a better plan (one with more credits)
    #
    # That means the following actions should result in no credits:
    #   Subscriber cancels and signs up for the same plan
    #   Subscriber downgrades to a worse plan
    #
    # This method is still cheatable by signing up for a free trial on a plan,
    # and then upgrading to a higher plan. However, only a small amount of
    # users will do this, and once their subscription runs out they will be
    # removed from the leaderboard.
    #
    # I feel like it's better to allow them to temporarily cheat the system
    # instead of adding subscription credits during the invoicing phase which
    # will mean that honest people who subscribe won't be able to get their
    # credits until after the free trial period.
    previous_plan_credits = 0
    plan_credits = plan["metadata"]["credits"]

    if previous_plan:
        previous_plan_credits = previous_plan["metadata"]["credits"]

    if cancelled_on is None and plan_credits == previous_plan_credits:
        credit_adjustment = plan_credits
    elif plan_credits <= previous_plan_credits:
        return credits
    else:
        # We only want to add the difference between upgrading plans,
        # because they were already credited the previous plan's credits.
        credit_adjustment = plan_credits - previous_plan_credits

    return credits + credit_adjustment
