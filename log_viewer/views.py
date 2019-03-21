# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from itertools import islice
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.admin.utils import (quote, unquote)
from django.utils.decorators import method_decorator

from log_viewer import settings
from log_viewer.utils import readlines_reverse


class LogViewerView(TemplateView):
    """
    LogViewerView class

    :cvar template_name: Name of the HTML template used to render the log files

    """
    template_name = "log_viewer/logfile_viewer.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LogViewerView, self).dispatch(*args, **kwargs)

    def get_context_data(self, file_name=None, page=1, **kwargs):
        """
        Read and return log files to be showed in admin page

        :param file_name: log file name
        :param page: log viewer page
        """
        context = super(LogViewerView, self).get_context_data(**kwargs)

        # Clean the `file_name` to avoid relative paths.
        file_name = unquote(file_name).replace('/..', '').replace('..', '')
        file_urls = []
        file_names = []
        file_display = []
        page = int(page)
        current_file = file_name

        lines_per_page = settings.LOG_VIEWER_ITEMS_PER_PAGE
        context['custom_file_list_title'] = settings.LOG_VIEWER_FILE_LIST_TITLE
        context['custom_style_file'] = settings.LOG_VIEWER_FILE_LIST_STYLES
        context['original_file_name'] = file_name
        context['next_page'] = page + 1
        context['log_files'] = []

        len_logs_dir = len(settings.LOG_VIEWER_FILES_DIR)

        for root, _, files in os.walk(settings.LOG_VIEWER_FILES_DIR):
            tmp_names = list(filter(lambda x: x.find('~') == -1, files))
            # if LOG_VIEWER_FILES is not set in settings
            # then all the files with '.log' extension are listed
            if len(settings.LOG_VIEWER_FILES) > 0:
                tmp_names = list(filter(lambda x: x in settings.LOG_VIEWER_FILES, tmp_names))
            else:
                tmp_names = [name for name in tmp_names if (name.split('.')[-1]) == 'log']
            file_names += tmp_names
            file_display += [('%s/%s' % (
                root[len_logs_dir:], name))[1:] for name in tmp_names]
            file_urls += list(map(lambda x: '%s/%s' % (root, x), tmp_names))

        for i, element in enumerate(file_display):
            context['log_files'].append({
                quote(element): {
                    'uri': file_urls[i],
                    'display': element,
                }
            })

        if file_name:
            try:
                with open(os.path.join(settings.LOG_VIEWER_FILES_DIR, file_name)) as file:
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
            except (IOError, ValueError):
                pass
        else:
            context['last'] = True

        if len(context['log_files']) > 0:
            context['log_files'] = sorted(context['log_files'],
                                          key=lambda x: sorted(x.items()))
        return context


log_viewer = LogViewerView.as_view()
