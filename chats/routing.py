
from django.urls import path
from .consumers import ChatChannel
urlpatterns=[
    path("chat/",ChatChannel.as_asgi(),)
]