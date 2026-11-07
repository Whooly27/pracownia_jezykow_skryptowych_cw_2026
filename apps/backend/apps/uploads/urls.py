from django.urls import path

from . import blob_views, views

app_name = "uploads"

urlpatterns = [
    path("uploads", views.start_upload, name="start"),
    path("uploads/<uuid:upload_id>/complete", views.complete_upload, name="complete"),
    path("files/<uuid:file_id>/replace", views.replace_file, name="replace"),
    path("_blob/<path:key>", blob_views.blob, name="blob"),
]
