# mi_app/management/commands/eliminar_registros_antiguos.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from users.models import WhatsappUser

class Command(BaseCommand):
    help = 'Elimina registros de MiModelo creados hace más de 30 días'

    def handle(self, *args, **kwargs):
        fecha_limite = timezone.now() - timedelta(days=30)
        registros_eliminados = WhatsappUser.objects.filter(date_request__lt=fecha_limite).delete()
        self.stdout.write(
            self.style.SUCCESS(f'Se eliminaron {registros_eliminados[1]["users.WhatsaapUser"]} registros antiguos.')
        )