from django.contrib import admin
from .models import MessageAiUser, MessageTemplate, UploadExcelFile  
# Register your models here.
admin.site.register(MessageAiUser)
admin.site.register(MessageTemplate)
admin.site.register(UploadExcelFile)
