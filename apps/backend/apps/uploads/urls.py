from django.urls import path

from . import blob_views, views

app_name = "uploads"

urlpatterns = [
    path("uploads", views.start_upload, name="start"),
    path("_blob/<path:key>", blob_views.put_blob, name="put_blob"),
]
