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
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import serializers
from .models import Branch, Shift, AcademicSession, SchoolClass, Section, Subject
from .permissions import IsAdminWriteOrReadOnly


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


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ["id", "name", "address", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAdminWriteOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "address"]
    ordering_fields = ["name", "created_at"]


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = [
            "id",
            "name",
            "start_time",
            "end_time",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAdminWriteOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name"]
    ordering_fields = ["start_time", "name"]


class SchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = [
            "id",
            "name",
            "branch",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SchoolClassViewSet(viewsets.ModelViewSet):
    queryset = SchoolClass.objects.select_related("branch").all()
    serializer_class = SchoolClassSerializer
    permission_classes = [IsAdminWriteOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active", "branch"]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = [
            "id",
            "name",
            "school_class",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.select_related("school_class").all()
    serializer_class = SectionSerializer
    permission_classes = [IsAdminWriteOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active", "school_class"]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "code",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminWriteOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "created_at"]


class AcademicSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicSession
        fields = [
            "id",
            "year",
            "is_active",
            "is_current",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AcademicSessionViewSet(viewsets.ModelViewSet):
    queryset = AcademicSession.objects.all()
    serializer_class = AcademicSessionSerializer
    permission_classes = [IsAdminWriteOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["year"]
    ordering_fields = ["year", "created_at"]


# Combined options endpoint
class ClassOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = ["id", "name", "branch", "is_active"]


class SectionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "name", "school_class", "is_active"]


class ShiftOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ["id", "name", "start_time", "end_time", "is_active"]


class SessionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicSession
        fields = ["id", "year", "is_active", "is_current"]


class BranchDataSerializer(serializers.Serializer):
    classes = ClassOptionSerializer(many=True)
    sections = SectionOptionSerializer(many=True)
    shifts = ShiftOptionSerializer(many=True)
    sessions = SessionOptionSerializer(many=True)


class BranchDataView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(response=BranchDataSerializer)},
        summary="Get active classes, sections, shifts, sessions (branch data)",
    )
    def get(self, request):
        classes_qs = SchoolClass.objects.filter(is_active=True).select_related("branch").only("id", "name", "branch_id", "is_active")
        sections_qs = Section.objects.filter(is_active=True).select_related("school_class").only("id", "name", "school_class_id", "is_active")
        shifts_qs = Shift.objects.filter(is_active=True).only("id", "name", "start_time", "end_time", "is_active")
        sessions_qs = AcademicSession.objects.filter(is_active=True).only("id", "year", "is_active", "is_current")

        payload = {
            "classes": ClassOptionSerializer(classes_qs, many=True).data,
            "sections": SectionOptionSerializer(sections_qs, many=True).data,
            "shifts": ShiftOptionSerializer(shifts_qs, many=True).data,
            "sessions": SessionOptionSerializer(sessions_qs, many=True).data,
        }
        return Response(payload)
