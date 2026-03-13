from django.contrib.contenttypes.models import ContentType
from apps.core.models import LogEntry


class LogService:
    """
    Сервис записи логов системы.
    """

    @staticmethod
    def log(
        action_type,
        entity,
        user=None,
        description="",
        changes=None,
        ip_address=None,
    ):
        """
        Создаёт запись в журнале.
        """

        LogEntry.objects.create(
            user=user,
            action_type=action_type,
            entity_type=entity.__class__.__name__,
            entity_id=entity.pk,
            description=description,
            changes_json=changes,
            ip_address=ip_address,
        )