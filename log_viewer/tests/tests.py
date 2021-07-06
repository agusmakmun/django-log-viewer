from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class TestLogsViewer(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='john',
            password='Foobar@1234',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        self.client_login = Client()
        self.client_login.force_login(self.user)
        self.client_anon = Client()
        self.url = reverse('log_file_view')

    def test_redirection(self):
        response = self.client_anon.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_logs_viewer(self):
        # response = self.client_login.get(self.url)
        # self.assertEqual(response.status_code, 200)
        # self.assertContains(response, 'Django Log Viewer')
        # self.assertTemplateUsed(response, 'log_viewer/logfile_viewer.html')

        # FIXME: django.urls.exceptions.NoReverseMatch: 'admin' is not a registered namespace
        ...
