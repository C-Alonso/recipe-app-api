from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """Test: waiting for DB when DB is available"""
        # The ConnectionHandler would through an OperationalError
        # depending on whether the DB is available or not.
        # We will patch the behaviour of the ConnectionHandler.
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # Overwrite the behaviour.
            gi.return_value = True  # Available for the mock object.
            call_command('wait_for_db')  # We will create that command later.
            self.assertEqual(gi.call_count, 1)  # call_count -> mock object.

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):  # time sleep (eq. to the gi above)
        """Test: waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # It will simulate that it tries to connect to the DB 5 times,
            # and finally connects of the 6th attempt.
            # We use the mock side_effect to define what will happen
            # each time the mock is used.
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
