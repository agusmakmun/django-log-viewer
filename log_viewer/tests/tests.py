from django.test import TestCase


class SimpleTest(TestCase):

    def test_redirection(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
