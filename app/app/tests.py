from django.test import TestCase
from .calc import add, subtract


class CalcTest(TestCase):

    def test_add_numbers(self):
        self.assertEqual(add(2, 10), 12)

    def test_subtract_numbers(self):
        self.assertEqual(subtract(2, 10), -8)
