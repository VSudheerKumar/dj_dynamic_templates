from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver

import os, uuid

from .models import *

@receiver(post_delete, sender=MailTemplate)
def _template_delete(sender, instance, **kwargs):
    if instance.is_active:
        try:
            os.remove(instance.get_template_path())
        except FileNotFoundError:
            pass