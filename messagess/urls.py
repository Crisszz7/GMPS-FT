from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'messages-ai', views.MessageAiViewSet)
router.register(r'messages-templates', views.MessageTemplateViewSet)
router.register(r'upload-excel', views.UploadExcelFileViewSet)


urlpatterns = [
    path("webhook/", views.webhook_twilio_whatsapp_function, name="webhook-twilio-wpp"),
    path("send_approved/", views.approved, name="send_approved_message"),
]

urlpatterns += router.urls

# ✅ Solo para desarrollo (esto no es necesario en producción si usas NGINX o similar)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

