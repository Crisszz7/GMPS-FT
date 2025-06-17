from django.shortcuts import render, HttpResponse
from rest_framework import viewsets
from .models import WhatsappUser, PlaceTrigalUser, AdministerUser, UserHistory, UserReject
from .serializer import WhatsappUserSerializer, PlaceTrigalSerializer, AdministerUserSerializer, UserHistorySerializer, UserRejectSerializer
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter
import json, io, os
import pandas as pd

# ==========================
# ========== VIEWS =========
# ==========================

## @class WhatsappUserViewSet
#  @brief ViewSet para gestionar usuarios que se registran por WhatsApp.
#  @details Permite listar, crear, actualizar y eliminar usuarios. Filtra los registros según la sede del administrador autenticado.
@extend_schema(tags=["WhatsappUser"])
class WhatsappUserViewSet(viewsets.ModelViewSet):
    queryset = WhatsappUser.objects.all()
    serializer_class = WhatsappUserSerializer

    ## @brief Filtra usuarios por la sede del administrador autenticado.
    #  @return Lista filtrada de objetos WhatsappUser.
    def get_queryset(self):
        user = self.request.user
        user_place_id = user.place_to_administer.id
        return WhatsappUser.objects.filter(place_to_work=user_place_id)


## @class PlaceTrigalUserViewSet
#  @brief ViewSet para gestionar sedes (lugares).
#  @details Provee operaciones CRUD básicas.
@extend_schema(tags=["PlaceTrigal"])
class PlaceTrigalUserViewSet(viewsets.ModelViewSet):
    queryset = PlaceTrigalUser.objects.all()
    serializer_class = PlaceTrigalSerializer


## @class AdministerUserViewSet
#  @brief ViewSet para gestionar usuarios administradores del sistema.
@extend_schema(tags=["AdministerUser"])
class AdministerUserViewSet(viewsets.ModelViewSet):
    queryset = AdministerUser.objects.all()
    serializer_class = AdministerUserSerializer


## @class UserHistoryViewSet
#  @brief ViewSet para el historial de usuarios.
#  @details Guarda comentarios y eventos relacionados con cambios de estado o decisiones tomadas sobre usuarios.
@extend_schema(tags=["UserHistory"])
class UserHistoryViewSet(viewsets.ModelViewSet):
    queryset = UserHistory.objects.all()
    serializer_class = UserHistorySerializer


## @class LoginView
#  @brief Vista personalizada para iniciar sesión.
#  @details Autentica usuarios administradores, elimina el token anterior y crea uno nuevo.
@extend_schema(
    tags=["Auth"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ["username", "password"]
        }
    },
    responses={
        200: OpenApiParameter(name='token', type=str, description='Token de autenticación'),
        401: OpenApiParameter(name='message', type=str, description='Credenciales no válidas'),
    }
)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    ## @brief Autentica al usuario y genera un token.
    #  @param request Datos con `username` y `password`.
    #  @return Token y datos del usuario autenticado, o mensaje de error.
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            Token.objects.filter(user=user).delete()  # Elimina tokens anteriores
            token = Token.objects.create(user=user)
            login(request, user)

            sede = user.place_to_administer.name_place_trigal

            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'sede': sede,
                }
            })

        return Response({'message': 'Credenciales no válidas'}, status=status.HTTP_401_UNAUTHORIZED)


## @class LogoutView
#  @brief Vista para cerrar sesión.
#  @details Elimina el token del usuario autenticado y cierra la sesión.
@extend_schema(
    tags=["Auth"],
    responses={
        200: OpenApiParameter(name='message', type=str, description='Se ha cerrado la sesión correctamente'),
        400: OpenApiParameter(name='message', type=str, description='Token no encontrado')
    }
)
class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    ## @brief Cierra la sesión del usuario y elimina su token.
    #  @param request Petición del usuario autenticado.
    #  @return Mensaje de éxito o error si no se encontró token.
    def post(self, request):
        try:
            request.user.auth_token.delete()
        except:
            return Response({'message': 'Token no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        logout(request)
        return Response({'message': 'Se ha cerrado la sesión correctamente'})
    
    
# ========================================================================
#                               Funciones auxiliares
# ========================================================================

## \fn changue_applicant_place(request)
## \brief Cambia a un usuario de una sede a otra.
@csrf_exempt
@extend_schema(
    methods=["POST"],
    request=None,
    responses={"200": "Cambio exitoso"}
)
def changue_applicant_place(request):
    try:
        data = json.loads(request.body)
        new_sede = data["place"]
        users = data["applicants"]

        for user_id in users:
            WhatsappUser.objects.filter(id=user_id).update(place_to_work=new_sede)

        return HttpResponse("ok")
    except Exception as e:
        return HttpResponse("Ha ocurrido un error: " + str(e))


## \fn download_excel_function(request)
## \brief Descarga un archivo Excel con los datos de usuarios seleccionados.
@csrf_exempt
@extend_schema(
    methods=["POST"],
    request=None,
    responses={"200": "Excel generado correctamente"}
)
def download_excel_function(request):
    try:
        users = json.loads(request.body)["applicants"]
        d = WhatsappUser.objects.filter(id__in=users)

        df = pd.DataFrame(list(d.values("name", "address", "document", "experience", "phone_number", "work_type", "place_to_work")))

        df = df.rename(columns={
            "name": "Nombre",
            "address": "Direccion",
            "document": "Documento",
            "experience": "Experiencia",
            "phone_number": "Telefono",
            "work_type": "Tipo de Trabajo",
            "place_to_work": "Sede"
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


## \class DownloadCVAPIView
## \brief Descarga el CV del usuario en formato PDF/Word.
class DownloadCVAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[OpenApiParameter(name="pk", required=True, type=int)],
        responses={200: "Archivo enviado"}
    )
    def get(self, request, pk):
        try:
            user = WhatsappUser.objects.get(pk=pk)
            if not user.cv:
                raise Http404("El usuario no tiene CV.")

            file_path = user.cv.path
            if not os.path.exists(file_path):
                raise Http404("Archivo no encontrado.")

            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))

        except WhatsappUser.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)


## \class UserRejectAPIView
## \brief API para listar y registrar rechazos de usuarios.
class UserRejectAPIView(APIView):

    @extend_schema(responses=UserRejectSerializer)
    def get(self, request):
        user_place_id = self.request.user.place_to_administer.id
        users = UserReject.objects.filter(place=user_place_id)
        serialized_users = UserRejectSerializer(users, many=True)
        return Response({"users": serialized_users.data})

    @extend_schema(request=None, responses={"200": "Rechazo registrado correctamente"})
    def post(self, request):
        data = json.loads(request.body)
        user = WhatsappUser.objects.get(id=data["id"])

        user_rejected_before = UserReject.objects.filter(document=user.document).first()

        if not user_rejected_before:
            UserReject.objects.create(
                document=user.document,
                name=user.name,
                place=user.place_to_work,
                applications_to_job=user.number_attempts
            )
        else:
            user_rejected_before.applications_to_job += 1
            user_rejected_before.save()

        return Response({"message": "Rechazo registrado correctamente"}, status=status.HTTP_200_OK)


## \class UserHistoryAPIView
## \brief API para obtener y crear historiales de usuarios.
class UserHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=UserHistorySerializer)
    def get(self, request):
        user = request.user
        if hasattr(user, "place_to_administer"):
            histories = UserHistory.objects.filter(user__place_to_work_id=user.place_to_administer.id)
        else:
            histories = UserHistory.objects.all()

        serializer = UserHistorySerializer(histories, many=True)
        return Response(serializer.data)

    @extend_schema(request=None, responses={"200": "Historial creado correctamente"})
    def post(self, request):
        data = request.data
        user = WhatsappUser.objects.get(id=data["user"])
        comments = data["comments"]
        UserHistory.objects.create(user=user, comments=comments)
        return Response({"message": "Historial creado correctamente"})