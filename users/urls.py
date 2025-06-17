from django.urls import include, path, re_path
from rest_framework import routers
from . import views
from .views import LogoutView, LoginView, DownloadCVAPIView, UserRejectAPIView, UserHistoryAPIView
from rest_framework.authtoken.views import obtain_auth_token

# ==========================
# ========== ROUTER =========
# ==========================

router = routers.DefaultRouter()

## @brief Endpoint para usuarios registrados por WhatsApp.
router.register(r'whatsapp-users', views.WhatsappUserViewSet)

## @brief Endpoint para sedes o lugares registrados.
router.register(r'place-trigal-users', views.PlaceTrigalUserViewSet)

## @brief Endpoint para usuarios administradores del sistema.
router.register(r'administer-users', views.AdministerUserViewSet)

## @brief Endpoint para historial de usuarios archivados.
router.register(r'archived-users', views.UserHistoryViewSet, basename="archived-users")


# ==========================
# ========== URLPATTERNS =========
# ==========================

urlpatterns = [
    ## @brief Ruta para inicio de sesión personalizado.
    re_path('login/', LoginView.as_view(), name="login"),

    ## @brief Ruta para cierre de sesión con eliminación del token.
    path('logout/', LogoutView.as_view(), name='logout'),

    ## @brief Cambia el lugar de trabajo de un solicitante.
    path('changue-applicant-place/', views.changue_applicant_place, name='changue-applicant-place'),

    ## @brief Exporta los datos de los solicitantes en formato Excel.
    path('download-applicants/', views.download_excel_function, name='download-applicants'),

    ## @brief Descarga el archivo CV de un usuario específico.
    path('download-cv/<int:pk>/', DownloadCVAPIView.as_view(), name='download_cv'),

    ## @brief Lista el historial de usuarios archivados.
    path('archived-users/', UserHistoryAPIView.as_view()),

    ## @brief Rechaza un usuario (por ejemplo, una solicitud).
    path('reject-user/', UserRejectAPIView.as_view(), name='reject-user'),
]

# Añade las rutas del router
urlpatterns += router.urls
