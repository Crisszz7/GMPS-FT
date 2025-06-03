#un viewset como los de DRF sirven para crear la logica de multiples vistas (GET, POST, PUT, DELETE)

from django.shortcuts import render, HttpResponse
from rest_framework import viewsets
from .models import WhatsappUser, PlaceTrigalUser, AdministerUser
from .serializer import WhatsappUserSerializer, PlaceTrigalSerializer, AdministerUserSerializer
from django.contrib.auth import authenticate,login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import json
import pandas as pd
import io

# Usa ModelViewSet si necesitas CRUD sobre un modelo con poca lógica extra.

# Usa APIView si necesitas manejar procesos más personalizados: login, registro con lógica especial, filtros avanzados, notificaciones, etc.

# Create your views here.
class WhatsappUserViewSet(viewsets.ModelViewSet):
    queryset = WhatsappUser.objects.all()
    serializer_class = WhatsappUserSerializer

    def get_queryset(self):
        user = self.request.user
        user_place_id = user.place_to_administer.id
        return WhatsappUser.objects.filter(place_to_work = user_place_id)
    

class PlaceTrigalUserViewSet(viewsets.ModelViewSet):
    queryset = PlaceTrigalUser.objects.all()
    serializer_class = PlaceTrigalSerializer


class AdministerUserViewSet(viewsets.ModelViewSet):
    queryset = AdministerUser.objects.all()
    serializer_class = AdministerUserSerializer



class LoginView(APIView):
    permission_classes = [permissions.AllowAny]  # permite acceso sin login

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Eliminar token anterior (si existe)
            Token.objects.filter(user=user).delete()

            # Crear nuevo token
            token = Token.objects.create(user=user)

            login(request, user)

            print('sede :', user.place_to_administer)

            sede = user.place_to_administer.name_place_trigal

            return Response({
                'token': token.key,
                'user': {
                    'id' : user.id,
                    'username' : user.username,
                    'email' : user.email,
                    'sede' : sede,
                }
            })
        

        return Response({'message': 'Credenciales no válidas'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
            print("Auth user:", request.user) 
            try:
                request.user.auth_token.delete()
            except:
                return Response({'message': 'Token no encontrado'}, status=status.HTTP_400_BAD_REQUEST)
            
            logout(request)
            return Response({'message': 'Se ha cerrado la sesión correctamente'})


def changue_applicant_place(request):
    try:
        new_sede = json.loads(request.body)["place"]
        users= json.loads(request.body)["applicants"]

        for user_id in users:
            WhatsappUser.objects.filter(id=user_id).update(place_to_work=new_sede)

        return HttpResponse("ok")
    except Exception as e:
        return HttpResponse("Ha ocurrido un error: " + str(e)) 


def download_excel_function(request):
    try:
        users = json.loads(request.body)["applicants"]
        d = WhatsappUser.objects.filter(id__in=users)

        df =pd.DataFrame(list(d.values("name", "address", "document", "experience", "phone_number", "work_type", "place_to_work")))

        df = df.rename(columns={
                "name" : "Nombre",
                "address" : "Direccion",
                "document" : "Documento",
                "experience" : "Experiencia",
                "phone_number" : "Telefono",
                "work_type" : "Tipo de Trabajo",
                "place_to_work" : "Sede"
            })

        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Hoja1', index=False)

        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(), 
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
            
        response['Content-Disposition'] = 'attachment; filename=Postulantes.xlsx'
        return response

    except Exception as e:
        return HttpResponse("Ha ocurrido un error: " + str(e))