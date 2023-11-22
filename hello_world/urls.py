from django.conf import settings
from django.urls import path

from hello_world.views import HelloWorldView

urlpatterns = [
    path("", HelloWorldView.as_view(), name="hello-world"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
