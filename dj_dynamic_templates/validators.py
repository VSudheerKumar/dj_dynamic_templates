from django.apps import apps
from django.core.validators import ValidationError

from .models import *


def validate_app(app_name):
    if not apps.is_installed(app_name):
        raise ValidationError([{'app_name': f'{app_name} is not present in INSTALLED APPS'}])


