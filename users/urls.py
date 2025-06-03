from django.urls import include, path, re_path
from rest_framework import routers
from . import views
from .views import LogoutView, LoginView
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register(r'whatsapp-users', views.WhatsappUserViewSet)
router.register(r'place-trigal-users', views.PlaceTrigalUserViewSet)
router.register(r'administer-users', views.AdministerUserViewSet)

urlpatterns = [
    re_path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('changue-applicant-place/', views.changue_applicant_place, name='changue-applicant-place'),
    path('download-applicants/', views.download_excel_function, name='download-applicants'),
]

urlpatterns += router.urls