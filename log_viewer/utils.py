# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from fnmatch import fnmatch
from django.http import JsonResponse

from log_viewer import settings


def get_log_files(directory):
    result = {}
    for root, _, files in os.walk(directory):
        all_files = list(filter(lambda x: x.find('~') == -1, files))

        log_files = []
        log_files.extend(list(filter(lambda x: x in settings.LOG_VIEWER_FILES, all_files)))
        log_files.extend([x for x in all_files if fnmatch(x, settings.LOG_VIEWER_FILES_PATTERN)])

        log_dir = os.path.relpath(root, directory)
        if log_dir == '.':
            log_dir = ''

        result[log_dir] = list(set(log_files))
    return result


def readlines_reverse(qfile, exclude=''):
    """
    Read file lines from bottom to top
    """
    # support custom patterns (fixed issue #4)
    patterns = settings.LOG_VIEWER_PATTERNS
    reversed_patterns = [x[::-1] for x in patterns]

    qfile.seek(0, os.SEEK_END)
    position = qfile.tell()
    line = ''

    while position >= 0:
        qfile.seek(position)
        next_char = qfile.read(1)

        # original
        # if next_char == "\n" and line and line[-1] == '[':
        #     if exclude in line[::-1]:
        #         line = ''
        #     else:
        #         yield line[::-1]
        #         line = ''
        # else:
        #     line += next_char

        # modified
        if next_char == '\n' and line:
            if any([line.endswith(p) for p in reversed_patterns]):
                if exclude in line[::-1]:
                    line = ''
                else:
                    yield line[::-1]
                    line = ''
        else:
            line += next_char
        position -= 1
    yield line[::-1]


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context
