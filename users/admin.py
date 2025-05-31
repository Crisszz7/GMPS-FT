from django.contrib import admin
from .models import WhatsappUser, PlaceTrigalUser, AdministerUser

# Register your models here.
admin.site.register(WhatsappUser)
admin.site.register(AdministerUser)
admin.site.register(PlaceTrigalUser)