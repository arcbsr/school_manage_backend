from django.http import JsonResponse
from django.db import connection
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


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
