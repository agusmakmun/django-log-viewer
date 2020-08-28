=================
Django Log Viewer
=================

|pypi version| |license| |build status|

Django Log Viewer allows you to read log files in the admin page by using ``DataTables``.
This project was modified from: https://bitbucket.org/inkalabsinc/django-log-viewer

-----------------

.. image:: https://i.imgur.com/2BFzilV.png


Quick start
-----------

1. Django Log Viewer is available directly from `PyPI`_:

::

    pip install django-log-viewer


2. Add ``"log_viewer"`` to your ``INSTALLED_APPS`` setting like this

::

    INSTALLED_APPS = [
        ...
        "log_viewer",
    ]


3. Include the log viewer URLconf in your project ``urls.py`` like this

::

    path('admin/log_viewer/', include('log_viewer.urls')),


4. In your settings file create the following value

::

    LOG_VIEWER_FILES = ['logfile1', 'logfile2', ...]
    LOG_VIEWER_FILES_PATTERN = 'logfile*'
    LOG_VIEWER_FILES_DIR = os.path.join(BASE_DIR, '../logs')
    LOG_VIEWER_MAX_READ_LINES = 1000  # total log lines will be read
    LOG_VIEWER_PAGE_LENGTH = 25       # total log lines per-page
    LOG_VIEWER_PATTERNS = [']OFNI[', ']GUBED[', ']GNINRAW[', ']RORRE[', ']LACITIRC[']

    # Optionally you can set the next variables in order to customize the admin:

    LOG_VIEWER_FILE_LIST_TITLE = "Custom title"
    LOG_VIEWER_FILE_LIST_STYLES = "/static/css/my-custom.css"


5. Create/register the logging

::

    import logging
    logger = logging.getLogger('LoggerName')
    logger.info('The info message')
    logger.warning('The warning message')
    logger.error('The error message')

6. Deploy static files by running the command

::

    python manage.py collectstatic


7. Start the development server and visit http://127.0.0.1:8000/admin/log_viewer/


.. |pypi version| image:: https://img.shields.io/pypi/v/django-log-viewer.svg
   :target: https://pypi.python.org/pypi/django-log-viewer

.. |license| image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://raw.githubusercontent.com/agusmakmun/django-log-viewer/master/LICENSE

.. |build status| image:: https://travis-ci.org/agusmakmun/django-log-viewer.svg?branch=master
   :target: https://travis-ci.org/agusmakmun/django-log-viewer

.. _`PyPI`: https://pypi.python.org/pypi/django-log-viewer
