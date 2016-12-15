from django.apps import AppConfig

class DanceClubConfig(AppConfig):
    name = 'danceclub'
    verbose_name = "Dance Club"

    def ready(self):
        import danceclub.signals.handlers #noqa