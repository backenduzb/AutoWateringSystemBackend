from __future__ import annotations

from typing import Optional
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.middleware import BaseMiddleware


def get_anonymous_user():
    from django.contrib.auth.models import AnonymousUser
    return AnonymousUser()


@sync_to_async
def _get_user(user_id):
    from django.contrib.auth.models import AnonymousUser
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


def _get_token_from_scope(scope) -> Optional[str]:
    
    query = parse_qs(scope.get("query_string", b"").decode("utf-8"))
    token = query.get("token", [None])[0]
    if token:
        return token

    for key, value in scope.get("headers", []):
        if key.lower() == b"authorization":
            raw = value.decode("utf-8")
            parts = raw.split(" ", 1)
            if len(parts) == 2:
                return parts[1].strip()
            return raw.strip()
    return None


class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
        
        token = _get_token_from_scope(scope)
        scope["user"] = AnonymousUser()

        if token:
            try:
                # AccessToken yordamida tokenni tekshirish
                access_token = AccessToken(token)
                user_id = access_token.get('user_id')
                
                if user_id is not None:
                    scope["user"] = await _get_user(int(user_id))
            except (InvalidToken, TokenError, ValueError, KeyError):
                scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)