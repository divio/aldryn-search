from django.apps import AppConfig


class AldrynSearchConfig(AppConfig):
    name = 'aldryn_search'

    def ready(self):
        from . import conf  # noqa
