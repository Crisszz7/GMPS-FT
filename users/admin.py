from django.contrib import admin
from .models import WhatsappUser, PlaceTrigalUser, AdministerUser, UserHistory

# Register your models here.
admin.site.register(WhatsappUser)
admin.site.register(AdministerUser)
admin.site.register(PlaceTrigalUser)
admin.site.register(UserHistory)