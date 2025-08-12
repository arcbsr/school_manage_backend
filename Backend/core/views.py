from django.http import JsonResponse
from django.db import connection
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.serializers import Serializer, CharField
from rest_framework_simplejwt.tokens import RefreshToken


def db_health_view(_request):
    # Coerce values to strings to ensure JSON serializability (e.g., PosixPath)
    info = {
        'engine': str(connection.settings_dict.get('ENGINE')),
        'name': str(connection.settings_dict.get('NAME')),
        'host': str(connection.settings_dict.get('HOST')),
        'port': str(connection.settings_dict.get('PORT')),
        'user': str(connection.settings_dict.get('USER')),
    }
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1;')
            row = cursor.fetchone()
        info['status'] = 'ok' if row and int(row[0]) == 1 else 'unknown'
        info['vendor'] = str(getattr(connection, 'vendor', ''))
        server_version = getattr(getattr(connection, 'connection', None), 'server_version', None)
        if server_version is not None:
            info['server_version'] = str(server_version)
    except Exception as exc:
        info['status'] = 'error'
        info['error'] = str(exc)
    return JsonResponse(info)


class ProtectedHelloView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': 'Hello, authenticated user!',
            'user': request.user.username,
        })


class APIKeyHelloView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # If API key auth succeeded, request.user will be the api_key_client
        is_api_key = getattr(request.user, 'username', '') == 'api_key_client'
        return Response({
            'message': 'Hello via API key!' if is_api_key else 'Hello (unauthenticated)',
            'authed_via_api_key': is_api_key,
        })


class LogoutSerializer(Serializer):
    refresh = CharField(required=True, allow_blank=False)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token_str = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()
        except Exception as exc:  # noqa: BLE001 - return 400 for invalid token inputs
            raise ValidationError({"refresh": ["Invalid or already blacklisted token."]}) from exc

        return Response({"detail": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
