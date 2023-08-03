from django.apps import AppConfig


class DjMailerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dj_dynamic_templates'
    verbose_name = "DJ Dynamic Template"
    verbose_name_plural = verbose_name + "'s"

    def ready(self):
        import dj_dynamic_templates.signals
