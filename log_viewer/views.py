# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from fnmatch import fnmatch
from itertools import islice
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.contrib.auth.decorators import (login_required, user_passes_test)
from django.contrib.admin.utils import (quote, unquote)
from django.utils.decorators import method_decorator
from django.utils.functional import SimpleLazyObject

from log_viewer import settings
from log_viewer.utils import (readlines_reverse, JSONResponseMixin)


class LogJsonView(JSONResponseMixin, TemplateView):

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(LogJsonView, self).dispatch(*args, **kwargs)

    def get_log_json(self, original_context={}):
        context = {}
        page = original_context.get('page', 1)
        file_name = original_context.get('file_name')

        # Clean the `file_name` to avoid relative paths.
        file_name = unquote(file_name).replace('/..', '').replace('..', '')
        file_urls = []
        file_names = []
        file_display = []
        page = int(page)
        current_file = file_name

        lines_per_page = settings.LOG_VIEWER_MAX_READ_LINES
        context['original_file_name'] = file_name
        context['next_page'] = page + 1
        context['log_files'] = []

        len_logs_dir = len(settings.LOG_VIEWER_FILES_DIR)

        for root, _, files in os.walk(settings.LOG_VIEWER_FILES_DIR):
            all_files = list(filter(lambda x: x.find('~') == -1, files))

            log_files = []
            log_files.extend(list(filter(lambda x: x in settings.LOG_VIEWER_FILES, all_files)))
            log_files.extend([x for x in all_files if fnmatch(
                x, settings.LOG_VIEWER_FILES_PATTERN)])
            log_files = list(set(log_files))

            file_names.extend(log_files)
            file_display.extend([('%s/%s' % (root[len_logs_dir:], name))[1:] for name in log_files])
            file_urls.extend(list(map(lambda x: '%s/%s' % (root, x), log_files)))

        for i, element in enumerate(file_display):
            context['log_files'].append({
                quote(element): {
                    'uri': file_urls[i],
                    'display': element,
                }
            })

        if file_name:
            try:
                file_log = os.path.join(settings.LOG_VIEWER_FILES_DIR, file_name)
                with open(file_log, encoding='utf8', errors='ignore') as file:
                    next_lines = list(islice(readlines_reverse(file, exclude='Not Found'),
                                             (page - 1) * lines_per_page,
                                             page * lines_per_page))

                    if len(next_lines) < lines_per_page:
                        context['last'] = True
                    else:
                        context['last'] = False
                    context['logs'] = next_lines
                    context['current_file'] = current_file
                    context['file'] = file

            except Exception as error:
                print(error)
                pass
        else:
            context['last'] = True

        if len(context['log_files']) > 0:
            context['log_files'] = sorted(context['log_files'],
                                          key=lambda x: sorted(x.items()))

        return context

    def render_to_response(self, context, **response_kwargs):

        # to support Django 3.1.* (fixed issue #6)
        file_name = context.get('file_name')
        if isinstance(file_name, SimpleLazyObject):
            context = context['view'].kwargs

        log_json = self.get_log_json(context)

        if 'file' in log_json:
            log_json['file'] = log_json['file'].name

        if 'view' in context:
            del context['view']

        context.update(**log_json)
        return self.render_to_json_response(context, **response_kwargs)


class LogViewerView(TemplateView):
    """
    LogViewerView class

    :cvar template_name: Name of the HTML template used to render the log files

    """
    template_name = "log_viewer/logfile_viewer.html"

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(LogViewerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, file_name=None, page=1, **kwargs):
        """
        Read and return log files to be showed in admin page

        :param file_name: log file name
        :param page: log viewer page
        """
        context = super(LogViewerView, self).get_context_data(**kwargs)
        context['custom_file_list_title'] = settings.LOG_VIEWER_FILE_LIST_TITLE
        context['custom_style_file'] = settings.LOG_VIEWER_FILE_LIST_STYLES
        context['page_length'] = settings.LOG_VIEWER_PAGE_LENGTH
        return context


log_json = LogJsonView.as_view()
log_viewer = LogViewerView.as_view()
