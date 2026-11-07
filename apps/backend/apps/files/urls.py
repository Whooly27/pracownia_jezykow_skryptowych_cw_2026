from django.urls import path

from . import views

app_name = "files"

urlpatterns = [
    path("files", views.list_files, name="list"),
    path("files/<uuid:file_id>/rename", views.rename_file, name="rename"),
    path("files/<uuid:file_id>/delete", views.delete_file, name="delete"),
    path("files/<uuid:file_id>/remove-access", views.remove_access, name="remove_access"),
    path("files/<uuid:file_id>/download", views.download_file, name="download"),
]
