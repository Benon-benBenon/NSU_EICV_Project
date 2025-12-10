# mongo_app/urls.py
from django.urls import path
#from .Views import upload_single_entry
from . import Views

urlpatterns = [
    path('', Views.index, name='index'),
    path('get_child_options/', Views.get_child_options, name='get_child_options'),
    path('export_csv/', Views.export_csv, name='export_csv'),
    path('image/<str:file_id>/', Views.get_image, name='get_image'),
    path("upload-entry/", Views.upload_single_entry, name="upload_single_entry"),
]

