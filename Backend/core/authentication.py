from typing import Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions


class HeaderAPIKeyAuthentication(authentication.BaseAuthentication):
    """
    Simple header-based API key auth for service-to-service access.

    - Expects header: 'X-API-Key: <key>'
    - Valid keys are defined in settings.API_KEYS (list of strings)
    - Returns a dedicated low-privilege user for request.user
    """

    keyword: str = 'HTTP_X_API_KEY'

    def authenticate(self, request) -> Optional[Tuple[object, None]]:
        api_key = request.META.get(self.keyword)
        # If header absent, let other authenticators try
        if not api_key:
            return None

        valid_keys = getattr(settings, 'API_KEYS', []) or []
        if api_key not in valid_keys:
            raise exceptions.AuthenticationFailed(_('Invalid API key'))

        User = get_user_model()
        # Create/get a dedicated service user with no privileges
        user, created = User.objects.get_or_create(
            username='api_key_client',
            defaults={'is_staff': False, 'is_superuser': False},
        )
        return user, None


