from django.contrib import admin
from django.urls import path, include

from ..urls import urlpatterns as log_viewer_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("logs/", include("log_viewer.urls")),
]
urlpatterns += log_viewer_urlpatterns
