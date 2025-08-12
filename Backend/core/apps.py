from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self) -> None:
        # Ensure drf-spectacular extension classes are imported
        import core.schema  # noqa: F401
        return None
