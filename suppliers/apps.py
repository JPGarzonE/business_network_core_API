from django.apps import AppConfig


class CompaniesConfig(AppConfig):
    name = 'suppliers'

    def ready(self):
        import suppliers.signals