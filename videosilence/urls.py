# example/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from .views import index, upload_video, get_progress, delete_videos


urlpatterns = [
    path('', index, name='index'),
    path('upload/', upload_video, name='upload_video'),
    path('progress/', get_progress, name='get_progress'),
    path('delete_videos/', delete_videos, name='delete_videos'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
