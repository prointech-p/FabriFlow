from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'apps.core'
    verbose_name = 'Производство'

    def ready(self):
        import apps.core.signals.detail_signals
