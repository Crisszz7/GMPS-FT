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



