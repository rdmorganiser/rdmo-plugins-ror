from django.apps import AppConfig


class RDMORorConfig(AppConfig):
    name = 'rdmo_ror'
    verbose_name = 'ROR Plugin'

    def ready(self):
        from . import handlers  # noqa: F401
