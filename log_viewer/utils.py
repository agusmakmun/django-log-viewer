# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os


def readlines_reverse(qfile, exclude=''):
    """
    Read file lines from bottom to top
    """
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
            # pattern = "; |\[INFO\] |\[DEBUG\] |\[WARNING\] |\[ERROR\] |\[CRITICAL\] "
            patterns = [']OFNI[', ']GUBED[', ']GNINRAW[', ']RORRE[', ']LACITIRC[']

            if any([line.endswith(p) for p in patterns]):
                if exclude in line[::-1]:
                    line = ''
                else:
                    yield line[::-1]
                    line = ''
        else:
            line += next_char
        position -= 1
    yield line[::-1]
