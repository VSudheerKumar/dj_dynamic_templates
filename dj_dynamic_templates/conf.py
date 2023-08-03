from django.conf import settings

import os
import  warnings

RECYCLE_PATH = None

if hasattr(settings, 'DJ_DYNAMIC_TEMPLATES'):
    RECYCLE_PATH = settings.DJ_DYNAMIC_TEMPLATES.get('recycle_path', None)

if RECYCLE_PATH:
    if not os.path.exists(RECYCLE_PATH):
        warnings.warn('Improperly configured RECYCLE PATH')
        RECYCLE_PATH = None
