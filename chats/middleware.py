from channels.middleware import BaseMiddleware
from django.db import close_old_connections
from django.contrib.auth.models import AnonymousUser
from jwt import decode as jwt_decode
from channels.db import database_sync_to_async
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication



class JwtAuthMiddleware(BaseMiddleware):

    def __init__(self,inner) -> None:
        super().__init__()
        self.inner=inner

    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass