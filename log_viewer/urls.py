# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django

from .views import log_viewer


if django.VERSION >= (2, 0):
    from django.urls import re_path
    urlpatterns = [
        re_path(r'^(?P<file_name>[\.\w-]*)/(?P<page>[0-9]+)', log_viewer, name='logfile-view'),
        re_path(r'^(?P<file_name>[\.\w-]*)', log_viewer, name='logfile-view'),
        re_path(r'^', log_viewer, name='logfile-view'),
    ]
else:
    from django.conf.urls import url
    urlpatterns = [
        url(r'^(?P<file_name>[\.\w-]*)/(?P<page>[0-9]+)', log_viewer, name='logfile-view'),
        url(r'^(?P<file_name>[\.\w-]*)', log_viewer, name='logfile-view'),
        url(r'^', log_viewer, name='logfile-view'),
    ]
