"""
ASGI config for sparrow project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from chats.middleware import JwtAuthMiddleware
from django.core.asgi import get_asgi_application
from chats.routing import websocket_urlpatterns


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sparrow.settings')

django_asgi_app = get_asgi_application()


applications=ProtocolTypeRouter({
    "http":django_asgi_app,
    "websocket":AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            JwtAuthMiddleware(
                URLRouter(websocket_urlpatterns)
            )
        )
    )
})
