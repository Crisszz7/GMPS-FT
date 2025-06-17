from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

# ==========================
# ========== ROUTER =========
# ==========================

router = routers.DefaultRouter()

## @brief Endpoint para gestión de mensajes generados por IA.
router.register(r'messages-ai', views.MessageAiViewSet)

## @brief Endpoint para plantillas de mensajes.
router.register(r'messages-templates', views.MessageTemplateViewSet)

## @brief Endpoint para subir archivos Excel que contienen datos para envíos masivos.
router.register(r'upload-excel', views.UploadExcelFileViewSet)


# ==========================
# ========== URLPATTERNS =========
# ==========================

urlpatterns = [
    ## @brief Webhook que recibe y procesa mensajes entrantes de Twilio WhatsApp.
    path("webhook/", views.webhook_twilio_whatsapp_function, name="webhook-twilio-wpp"),

    ## @brief Envía mensajes de aprobación a los usuarios seleccionados.
    path("send_approved/", views.approved, name="send_approved_message"),

    ## @brief Envía mensajes de marketing en masa.
    path("send_marketing/", views.send_marketing_message, name="send_marketing_function"),
]

# Añade las rutas del router
urlpatterns += router.urls

## @brief Habilita la carga de archivos multimedia en desarrollo.
#  @details Esto sirve para servir archivos desde MEDIA_URL durante el desarrollo. En producción, se usa un servidor como NGINX.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

