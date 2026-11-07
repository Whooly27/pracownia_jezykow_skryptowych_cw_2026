from django.urls import path

from . import views

app_name = "files"

urlpatterns = [
    path("files", views.list_files, name="list"),
    path("files/<uuid:file_id>/rename", views.rename_file, name="rename"),
]
