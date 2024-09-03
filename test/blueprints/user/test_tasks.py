from neurone.blueprints.user.models import User
from neurone.blueprints.user.tasks import deliver_password_reset_email
from neurone.extensions import mail


class TestTasks(object):
    def test_deliver_password_reset_email(self, token):
        """Deliver a password reset email."""
        with mail.record_messages() as outbox:
            user = User.find_by_identity("marco.colonna@zoho.eu")
            deliver_password_reset_email.run(user.id, token)

            assert len(outbox) == 1
            assert token in outbox[0].body
