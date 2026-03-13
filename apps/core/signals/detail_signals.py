from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.core.models import Detail
from apps.core.services.log_service import LogService


@receiver(post_save, sender=Detail)
def log_detail_save(sender, instance, created, **kwargs):

    if created:

        LogService.log(
            action_type="CREATE",
            entity=instance,
            description=f"Создана деталь {instance.article}"
        )

    else:

        LogService.log(
            action_type="UPDATE",
            entity=instance,
            description=f"Изменена деталь {instance.article}"
        )