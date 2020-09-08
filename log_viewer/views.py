# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import zipfile
from io import BytesIO
from itertools import islice

from django.http import HttpResponse, Http404
from django.views.generic import TemplateView as _TemplateView
from django.contrib.auth.decorators import (login_required, user_passes_test)
from django.contrib.admin.utils import (quote, unquote)
from django.utils.decorators import method_decorator
from django.utils.functional import SimpleLazyObject
from django.utils.timezone import localtime, now
from django.conf import settings as django_settings
from log_viewer import settings
from log_viewer.utils import (get_log_files, readlines_reverse, JSONResponseMixin)


class TemplateView(_TemplateView):

    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(TemplateView, self).dispatch(*args, **kwargs)


class LogJsonView(JSONResponseMixin, TemplateView):

    def get_log_json(self, original_context={}):
        context = {}
        page = original_context.get('page', 1)
        file_name = original_context.get('file_name', '')

        # Clean the `file_name` to avoid relative paths.
        file_name = unquote(file_name).replace('/..', '').replace('..', '')
        page = int(page)
        current_file = file_name

        lines_per_page = settings.LOG_VIEWER_MAX_READ_LINES
        context['original_file_name'] = file_name
        context['next_page'] = page + 1
        context['log_files'] = []

        log_file_data = get_log_files(settings.LOG_VIEWER_FILES_DIR)
        for log_dir, log_files in log_file_data.items():
            for log_file in log_files:
                display = os.path.join(log_dir, log_file)
                uri = os.path.join(settings.LOG_VIEWER_FILES_DIR, display)

                context['log_files'].append({
                    quote(display): {
                        'uri': uri,
                        'display': display,
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


class LogDownloadView(TemplateView):

    def render_to_response(self, context, **response_kwargs):
        # file_name = context.get('file_name', None)
        file_name = self.request.GET.get('file_name', None)
        log_file_result = get_log_files(settings.LOG_VIEWER_FILES_DIR)

        if file_name:
            file_path = unquote(file_name)
            uri = os.path.join(settings.LOG_VIEWER_FILES_DIR, file_path)

            log_dir = os.path.dirname(file_path)
            log_file = os.path.basename(file_path)

            if log_file in log_file_result.get(log_dir, []):
                with open(uri, 'rb') as f:
                    buffer = f.read()
                resp = HttpResponse(buffer, content_type='plain/text')
                resp['Content-Disposition'] = 'attachment; filename=%s' % file_name
                return resp
            else:
                raise Http404

        else:
            generation_time = localtime() if django_settings.USE_TZ else now()
            zip_filename = 'log_%s.zip' % generation_time.strftime("%Y%m%dT%H%M%S")
            zip_buffer = BytesIO()

            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                for log_dir, log_files in log_file_result.items():
                    for log_file in log_files:
                        display = os.path.join(log_dir, log_file)
                        uri = os.path.join(settings.LOG_VIEWER_FILES_DIR, display)

                        with open(uri, 'r') as f:
                            zip_file.writestr('%s' % display, f.read())

            zip_buffer.seek(0)
            resp = HttpResponse(zip_buffer, content_type='application/zip')
            resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
            return resp


class LogViewerView(TemplateView):
    """
    LogViewerView class

    :cvar template_name: Name of the HTML template used to render the log files

    """
    template_name = "log_viewer/logfile_viewer.html"

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
log_download = LogDownloadView.as_view()
