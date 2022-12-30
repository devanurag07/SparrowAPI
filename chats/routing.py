
from django.urls import path
from .consumers import ChatChannel
websocket_urlpatterns=[
    path("chat/",ChatChannel.as_asgi(),)
]