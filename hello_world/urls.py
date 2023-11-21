from django.urls import path

from hello_world.views import HelloWorldView

urlpatterns = [
    path("", HelloWorldView.as_view(), name="hello-world"),
]
