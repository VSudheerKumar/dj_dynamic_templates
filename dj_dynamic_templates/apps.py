from django.apps import AppConfig


class DjMailerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dj_dynamic_templates'

    def ready(self):
        import dj_dynamic_templates.signals
