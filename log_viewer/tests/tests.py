import os
import types
import tempfile
from itertools import islice

from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..utils import get_log_files, readlines_reverse

User = get_user_model()


class TestLogsViewer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="john",
            password="Foobar@1234",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        self.client_login = Client()
        self.client_login.force_login(self.user)
        self.client_anon = Client()
        self.url = reverse("log_file_view")

    def test_redirection(self):
        response = self.client_anon.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_logs_viewer(self):
        response = self.client_login.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Log Viewer")
        self.assertTemplateUsed(response, "log_viewer/logfile_viewer.html")

    def test_get_log_files(self):
        with tempfile.TemporaryDirectory() as parent_level_log_dir, \
                tempfile.TemporaryDirectory(dir=parent_level_log_dir) as child_one_log_dir, \
                tempfile.TemporaryDirectory(dir=parent_level_log_dir) as child_two_log_dir:
            open("%s/default.log" % parent_level_log_dir, "a").close()
            open("%s/a.log" % child_one_log_dir, "a").close()
            open("%s/b.log" % child_two_log_dir, "a").close()

            child_one_relative_path = os.path.relpath(child_one_log_dir, parent_level_log_dir)
            child_two_relative_path = os.path.relpath(child_two_log_dir, parent_level_log_dir)

            result = get_log_files(parent_level_log_dir, 2, 1)
            self.assertEqual(
                result,
                {
                    "logs": {
                        "": ["default.log"],
                        child_one_relative_path: ["a.log"],
                        child_two_relative_path: ["b.log"],
                    },
                    "next_page_files": 2,
                    "last_files": True,
                },
            )

    def test_readlines_reverse(self):
        with tempfile.TemporaryDirectory() as log_dir:
            with open("%s/default.log" % log_dir, "w") as qfile:
                qfile.write(
                    "[WARNING] 2022-08-26 13:02:46,070 django.request: Not Found: /404/"
                )
                qfile.write(
                    "[ERROR] 2022-08-26 13:02:50,962 django.request: Internal Server Error: /admin/"
                )
                qfile.write(
                    "[INFO] 2022-08-26 13:02:36,604 django.utils.autoreload: Watching for file changes"
                )
                qfile.close()

            with open(
                "%s/default.log" % log_dir, encoding="utf8", errors="ignore"
            ) as qfile:
                lines = readlines_reverse(qfile, exclude=None)
                lines_string = " ".join(map(str, lines))
                self.assertTrue(isinstance(lines, types.GeneratorType))
                self.assertIn("[WARNING]", lines_string)
                self.assertIn("[ERROR]", lines_string)
                self.assertIn("[INFO]", lines_string)
