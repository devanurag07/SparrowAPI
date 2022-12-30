"""
ASGI config for sparrow project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from chats.consumers import TestChannel
from django.urls import path
from channels.auth import AuthMiddlewareStack
from chats.routing import websocket_urlpatterns
from chats.middleware import JwtAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sparrow.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http":
    get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            JwtAuthMiddleware(
                URLRouter(websocket_urlpatterns))
        )
    ),
})
