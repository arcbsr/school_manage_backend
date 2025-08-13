from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self) -> None:
        # Ensure drf-spectacular extension classes are imported
        import core.schema  # noqa: F401
        # Create default admin user from environment variables if provided
        from django.db.models.signals import post_migrate
        from django.contrib.auth import get_user_model
        from decouple import config as env_config

        def _create_default_admin(*_args, **_kwargs):
            username = env_config('ADMIN_USERNAME', default='')
            email = env_config('ADMIN_EMAIL', default='')
            password = env_config('ADMIN_PASSWORD', default='')
            if not username or not password:
                return
            User = get_user_model()
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, email=email, password=password)

        # Run after migrations
        post_migrate.connect(_create_default_admin, dispatch_uid='core.create_default_admin')
        # Also attempt once at startup (safe & idempotent)
        try:
            _create_default_admin()
        except Exception:
            pass
        return None
