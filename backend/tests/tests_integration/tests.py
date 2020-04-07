from django.urls import reverse
from django.core.exceptions import ValidationError
from django.test import TestCase


class TrucTestCase(TestCase):
    def test_true(self):
        response = 200
        self.assertEqual(response,200)

