from unittest.mock import patch

from django.test import TestCase
from django.db.utils import OperationalError
from django.core.management import call_command


class CommandsTest(TestCase):

    def test_wait_for_db_successful(self):
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db_fail_5_times_then_successful(self, ts):
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
