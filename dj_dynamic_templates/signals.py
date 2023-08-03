import datetime

from django.db.models.signals import post_delete, pre_save, post_save, pre_delete
from django.dispatch import receiver

import os
import shutil

from .models import *
from .utils import file_or_dir_remove_signal
from .conf import *

@receiver(post_delete, sender=MailTemplate)
def _template_delete(sender, instance, **kwargs):
    if instance.is_active:
        try:
            os.remove(instance.get_template_path())
        except FileNotFoundError:
            pass

@receiver(file_or_dir_remove_signal)
def _file_or_dir_remove_signal(sender, path=None, **kwargs):
    if RECYCLE_PATH:
        dest = False
        if os.path.isdir(path):
            dest = shutil.copytree(path, RECYCLE_PATH + f"{datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')} - {kwargs.get('name', ' ')}")
        if os.path.isfile(path):
            dest = shutil.copyfile(path, RECYCLE_PATH + f"{kwargs.get('id', ' ')} - {kwargs.get('name', ' ')} - {'re synced' if kwargs.get('re_sync') else 'changed'} - {datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')}.html")
        return dest
    return None
