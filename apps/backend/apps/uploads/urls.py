from django.urls import path

from . import blob_views

app_name = "uploads"

urlpatterns = [
    path("_blob/<path:key>", blob_views.put_blob, name="put_blob"),
]
