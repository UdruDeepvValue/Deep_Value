from neurone.blueprints.billing.models.subscription import Subscription
from neurone.blueprints.user.models import User


class TestUser(object):
    def test_serialize_token(self, token):
        """Token serializer serializes a token correctly."""
        assert token.count(".") == 2

    def test_find_by_token_token(self, token):
        """Token de-serializer de-serializes a token correctly."""
        user = User.find_by_token(token)
        assert user.email == "marco.colonna@zoho.eu"

    def test_find_by_token_tampered(self, token):
        """Token de-serializer returns None when it's been tampered with."""
        user = User.find_by_token("{0}1337".format(token))
        assert user is None

    def test_subscribed_user_receives_more_credits(self, users):
        """Subscribed user receives more credits."""
        user = User.find_by_identity("marco@deep-value.cloud")
        user.add_credits(Subscription.get_plan_by_id("gold"))

        assert user.credits == 210
