from django.urls import path
from .views import process_get_view, user_form, handle_file_upload, handle_limited_file_upload


app_name = 'requestdataapp'

urlpatterns = [
    path('get/', process_get_view, name='get-view'),
    path('bio/', user_form, name='user-form'),
    path('upload/', handle_file_upload, name='file_upload'),
    path('limited_upload/', handle_limited_file_upload, name='file_limited_upload'),
]