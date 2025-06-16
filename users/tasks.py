# mi_app/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from users.models import WhatsappUser

@shared_task
def eliminar_registros_antiguos():
    fecha_limite = timezone.now() - timedelta(days=30)
    registros_eliminados = WhatsappUser.objects.filter(date_request__lt=fecha_limite).delete()
    return f'Se eliminaron {registros_eliminados[1]["users.WhatsappUser"]} registros antiguos.'