from time import sleep

from flask import json
from flask import url_for

from lib.tests import ViewTestMixin
from lib.tests import assert_status_with_message


# Aggiungere tests per neurone
class TestBetting(ViewTestMixin):
    def testNeurone(self):
        pass