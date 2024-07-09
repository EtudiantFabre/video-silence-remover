# example/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from example.views import index, upload_video


urlpatterns = [
        path('', index, name='index'),
        #path('upload/', upload_video, name='upload_video'),
]# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)