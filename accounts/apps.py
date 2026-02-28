from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # Импорт сигналов в ready гарантирует, что они подключатся ровно при запуске приложения.
        import accounts.signals  # noqa: F401
