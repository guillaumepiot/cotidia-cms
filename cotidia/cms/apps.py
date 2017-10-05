from django.apps import AppConfig


class CMSConfig(AppConfig):
    name = "cotidia.cms"
    label = "cms"

    def ready(self):
        import cotidia.cms.signals
