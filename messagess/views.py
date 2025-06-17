## @file views.py
#  @brief Vista principal para el manejo de mensajes, plantillas y archivos Excel en la app.
#  Contiene endpoints de Django REST Framework y funciones auxiliares para procesamiento de mensajes con Twilio y Gemini.

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from rest_framework import viewsets, status
from .models import MessageAiUser, MessageTemplate, UploadExcelFile
from users.models import WhatsappUser, PlaceTrigalUser, UserHistory
from .serializer import MessageAiSerializer, MessageTemplateSerializer, UploadExcelFileSerializer
from users.serializer import WhatsappUserSerializer
from django.conf import settings
from django.http import HttpResponse
from twilio.request_validator import RequestValidator
import logging
from .utils import save_files_applicants_function, ai_validator_file_function
from google import genai
from google.genai import types
import json
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from users.serializer import UserHistorySerializer
from django.shortcuts import get_object_or_404
import pandas as pd
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

# ==========================
# ========== VIEWS =========
# ==========================


## @class MessageAiViewSet
#  @brief ViewSet para el modelo MessageAiUser.
class MessageAiViewSet(viewsets.ModelViewSet):
    queryset = MessageAiUser.objects.all()
    serializer_class = MessageAiSerializer


## @class UploadExcelFileViewSet
#  @brief ViewSet para subir archivos Excel.
class UploadExcelFileViewSet(viewsets.ModelViewSet):
    queryset = UploadExcelFile.objects.all()
    serializer_class = UploadExcelFileSerializer

    ## @brief Filtra los archivos por el lugar asociado al usuario autenticado.
    def get_queryset(self):
        user = self.request.user
        user_place_id = user.place_to_administer.id
        return UploadExcelFile.objects.filter(place=user_place_id)


## @class MessageTemplateViewSet
#  @brief ViewSet para las plantillas de mensajes.
class MessageTemplateViewSet(viewsets.ModelViewSet):
    queryset = MessageTemplate.objects.all()
    serializer_class = MessageTemplateSerializer

    ## @brief Filtra las plantillas por el lugar asociado al usuario autenticado.
    def get_queryset(self):
        user = self.request.user
        user_place_id = user.place_to_administer.id
        return MessageTemplate.objects.filter(place=user_place_id)

    ## @brief Guarda la plantilla asignando el lugar del usuario automáticamente.
    #  @param serializer El serializer con los datos validados.
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(place=user.place_to_administer)


# ========================================================================
#                               Funciones auxiliares
# ========================================================================


## @fn billy_asesor_function
#  @brief Interactúa con la API de Gemini para obtener una respuesta automática basada en preguntas frecuentes.
#  @param body_message Mensaje enviado por el usuario.
#  @return Una respuesta generada por IA o mensaje de error.
def billy_asesor_function(body_message):
    list_messages = MessageAiUser.objects.all().values_list('ask', 'answer')

    messages = "\n\n".join([f"[{i+1}] Respuesta:{answer} \n Pregunta:{ask} \n\n " for i, (ask, answer) in enumerate(list_messages)])
    print(messages)

    context = f"Listado de preguntas: {messages}\n\nUsuario pregunta:{body_message}"

    client = genai.Client(api_key=settings.API_KEY_GEMINI)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction="Eres un asistente que responde basado en un listado de preguntas y respuestas. Dara una respuesta que coincida o se asemeje. Si la pregunta no coincide con ninguna del listado, di: 'Para una pregunta detallada, un asesor te contactará (horario: 6:00 am - 2:30 pm)'.",
                temperature=0.3,
                max_output_tokens=200,
            ),
            contents=context
        )

        return response.text

    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}", exc_info=True)
        return "Un error ha ocurrido, intenta esta opción más tarde."


## @fn webhook_twilio_whatsapp_function
#  @brief Función que actúa como webhook de Twilio para recibir mensajes de WhatsApp.
#  @param request Objeto HttpRequest con los datos del mensaje recibido.
#  @return HttpResponse con una respuesta TwiML (texto XML).
@csrf_exempt
def webhook_twilio_whatsapp_function(request):
    try:
        validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
        url = request.build_absolute_uri().replace("http://", "https://")
        signature = request.META.get('HTTP_X_TWILIO_SIGNATURE', '')

        if not validator.validate(url, request.POST, signature):
            return HttpResponse("Invalid Request", status=403)

        body_message = request.POST.get('Body', '')
        user_sender = request.POST.get('From', '')
        media_type = request.POST.get('MediaContentType0')
        media_url = request.POST.get('MediaUrl0')
        profile_name = request.POST.get('ProfileName', '')

        user, created = WhatsappUser.objects.get_or_create(phone_number=user_sender)
        response = send_message_whatsapp_function(body_message, user, media_type, media_url, profile_name)
        return HttpResponse(str(response), content_type="text/xml")

    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}", exc_info=True)
        response = MessagingResponse()
        response.message("Un error ha ocurrido, intenta esta opción más tarde")
        return HttpResponse(str(response), content_type="text/xml")

##
# @brief Envía un mensaje de respuesta por WhatsApp utilizando Twilio.
#
# Esta función evalúa el tipo de entrada del usuario (texto o archivo multimedia) y responde
# en consecuencia utilizando la lógica definida en `process_user_input_function`.
#
# @param body_message Mensaje de texto enviado por el usuario.
# @param user Objeto de usuario que contiene el estado actual de la conversación.
# @param media_type Tipo de archivo multimedia recibido (ej. image/jpeg, application/pdf).
# @param media_url URL del archivo multimedia.
# @param profile_name Nombre del perfil que envía el mensaje.
#
# @return Un objeto `MessagingResponse` con la respuesta generada.
##
def send_message_whatsapp_function(body_message, user, media_type, media_url, profile_name):

    response = MessagingResponse()

    if body_message.strip():
        print("body_message")
        reply = process_user_input_function(user, body_message, media_url, media_type, profile_name)
        response.message(reply)
    elif media_url:
        print("media_url")
        reply = process_user_input_function(user, body_message, media_type, media_url, profile_name)
        response.message(reply)
    else:
        response.message("Lo siento, no entendí tu mensaje. Por favor, intenta de nuevo.")

    return response

    
##
# @brief Procesa la entrada del usuario y determina la respuesta correspondiente.
#
# Esta función gestiona el flujo de conversación en función del estado del usuario
# y del contenido recibido (texto o archivo). Permite aceptar políticas de datos,
# aplicar a trabajos o hacer preguntas.
#
# @param user Objeto de usuario que contiene el estado actual y datos relacionados.
# @param body_message Texto enviado por el usuario.
# @param media_type Tipo de archivo enviado, si existe.
# @param media_url URL del archivo enviado, si existe.
# @param profile_name Nombre del perfil del remitente.
#
# @return Un string con el mensaje de respuesta adecuado para el usuario.
#
# @note Cambia el estado del usuario según la interacción.
# @note Valida y guarda archivos cuando son enviados por el usuario.
##
def process_user_input_function(user, body_message, media_type, media_url, profile_name):


    print("process_user_input_function")
    if user.state is None or body_message.lower().strip() == "hola":
        user.state = "habeas-data"
        user.save()
        print("habeas-data")
        return (
                "Hola 👋, Soy tu asistente virtual para *Flores El Trigal*. \n"
                "Te ayudare para los servicios disponibles de nuestra empresa por este chat. \n\n"
                "Para empezar, te solicitamos aceptar nuestro tratamiento y uso de datos personales, *puedes conocerlo en este enlace*: https://n9.cl/zl141 \n\n"
                "Digita el numero a continuación :\n"
                "1-  Acepto \n"
                "2-  No Acepto "
            )

    
    if user.state == "habeas-data" or body_message.lower().strip() == "inicio":
        if body_message.strip() == "1" or body_message.lower().strip() == "inicio":
            user.state = "work-ask-media"
            user.save()
            print("work-ask-media")
            return(
                "Selecciona el servicio que requieras: \n\n"
                "1-  Aplicar a una oferta laboral \n"
                "2-  Preguntas e inquietudes \n\n"
                "*Si tienes tu hoja de vida ya lista, enviala a travez de este chat 📄💼.* \n\n"
                "Puedes enviarla como un archivo PDF, Word o una imagen."
            )
        
        elif body_message.strip() == "2":
            user.state = None
            user.save()
            print("No has aceptado la politica de tratamiento de datos.")
            return(
                "No has aceptado la politica de tratamiento de datos. \n\n"
                "Procederé a finalizar este chat. \n\n"
                "Recuerda que puedes comunicarte con nosotros en cualquier momento 🌻😊."
            )
        else:
            print("Opcion No valida")
            return(
                "Opcion No valida. Recuerda selecionar 1️⃣ para *Aceptar* o 2️⃣ para *No aceptar*"
            )

    
    if user.state == "work-ask-media":
        if body_message.strip() == "1":
            user.state = "work-place"
            user.save()
            print("work-place")
            return(
                "Te socilito que digites la sede a la cual deseas aplicar. \n\n"
                "1️⃣ Aguas Claras - *Carmen de viboral*   🏠 \n"
                "2️⃣ Caribe - *San Antonio de Pereira, Rionegro*  🏠 \n"
                "️3️⃣ Manantiales - *La Ceja* 🏠 \n"
                "4️⃣ Olas - *Llanogrande, Rionegro*  🏠\n\n"
                "Si deseas volver al menu principal escribe inicio en cualquier momento"
            )

        elif body_message.strip() == "2":
            user.state = "ask"
            user.save()
            print("ask")
            return (
                "Por favor ahora, formula tu pregunta. *Billy* (nuestro asesor) 🧑‍💻, tratara de darte la respuesta mas adecuada. \n\n"
            )
        
        elif media_url:
            print("media_url")
            if media_type.startswith("image/"):
                print("image")
                response_ai_media = ai_validator_file_function(body_message, media_type, media_url, user)
                if response_ai_media == "True":
                    print("response_ai_media")
                    success, message = save_files_applicants_function(media_type, media_url, user, profile_name)
                    if success:
                        print("success")
                        user.state = "work-place-cv"
                        user.save()
                        return (
                            "Tu documento se ha guardado con exito \n\n"
                            "Te socilito que ahora digites la sede a la cual deseas aplicar con tu Archivo \n"
                            "1️⃣ Aguas Claras - *Carmen de viboral*   🏠 \n"
                            "2️⃣ Caribe - *San Antonio de Pereira, Rionegro*  🏠 \n"
                            "️3️⃣ Manantiales - *La Ceja* 🏠 \n"
                            "4️⃣ Olas - *Llanogrande, Rionegro*  🏠\n\n"  
                            "Si deseas volver al menu principal escribe inicio en cualquier momento"
                        )
                else:
                    print("else")
                    return(
                        "Lo siento, no es un archivo valido ☹️. \n\n"
                        "El sistema no reconocio tu archivo como una hoja de vida valida. Intenta de nuevo"
                    )
            elif media_type == "application/pdf":
                print("pdf")
                response_ai_media = ai_validator_file_function(body_message, media_type, media_url, user)
                if response_ai_media == "True":
                    print("response_ai_media")
                    success, message = save_files_applicants_function(media_type, media_url, user, profile_name)
                    if success:
                        print("success")
                        user.state = "work-place-cv"
                        user.save()
                        return (
                            "Tu documento se ha guardado con exito \n\n"
                            "Te socilito que ahora digites la sede a la cual deseas aplicar con tu Archivo \n"
                            "1️⃣ Aguas Claras - *Carmen de viboral*   🏠 \n"
                            "2️⃣ Caribe - *San Antonio de Pereira, Rionegro*  🏠 \n"
                            "️3️⃣ Manantiales - *La Ceja* 🏠 \n"
                            "4️⃣ Olas - *Llanogrande, Rionegro*  🏠\n\n"  
                        )
                else:
                    print("else")
                    return(
                        "Lo siento, no es un archivo valido ☹️. \n\n"
                        "El sistema no reconocio tu archivo como una hoja de vida valida."
                    )

            elif media_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                print("word")
                response_ai_media = ai_validator_file_function(body_message, media_type, media_url, user)
                if response_ai_media == "True":
                    print("response_ai_media")
                    success, message = save_files_applicants_function(media_type, media_url, user, profile_name)
                    if success:
                        print("success")
                        user.state = "work-place-cv"
                        user.save()
                        return (
                            "Tu documento se ha guardado con exito \n\n"
                            "Te socilito que ahora digites la sede a la cual deseas aplicar con tu Archivo \n"
                            "1️⃣ Aguas Claras - *Carmen de viboral*   🏠 \n"
                            "2️⃣ Caribe - *San Antonio de Pereira, Rionegro*  🏠 \n"
                            "️3️⃣ Manantiales - *La Ceja* 🏠 \n"
                            "4️⃣ Olas - *Llanogrande, Rionegro*  🏠\n\n"
                            "Si deseas volver al menu principal escribe inicio en cualquier momento"
                        )
                else:
                    print("else")
                    return(
                        "Lo siento, no es un archivo valido ☹️. \n\n"
                        "El sistema no reconocio tu archivo como una hoja de vida valida. Intenta de nuevo con otro archivo."
                    )
            else:
                print("else")
                return(
                    "No reconocozco el tipo de archivo ☹️. \n\n  "
                    "Recuerda que los formatos aceptados son: *PDF, Word o imagen.*"
                )
        else:
            return (
                "Opcion No valida. Recuerda selecionar 1️⃣ para *Oferta laboral* o 2️⃣ para *preguntas e inquietudes.*"
            )

    elif user.state == "work-place":
        if body_message in ["1", "2", "3", "4"]:
            if body_message == "1":
                place_id = 1
            elif body_message == "2":
                place_id = 2
            elif body_message == "3":
                place_id = 3
            elif body_message == "4":
                place_id = 4

            place = PlaceTrigalUser.objects.get(id=place_id)
            user.place_to_work = place
            user.state = "work-type"
            user.save()
            return (
                "Haz escogido tu sede 🏠✅. \n\n"
                "Escoge el tipo de oferta laboral disponible: \n\n"
                "1️⃣ Campo 🌿 \n"
                "2️⃣ Poscosecha 💐 \n"
                "3️⃣ Otro 💼 \n"
            )
        else:
            return (
                "Opcion No valida. Recuerda selecionar el numero de la oferta laboral disponible \n\n"
            )

    elif user.state == "work-place-cv" or user.work_type == "Dato no encontrado -IA":
        if body_message in ["1", "2", "3", "4"]:
            if body_message == "1":
                place_id = 1
            elif body_message == "2":
                place_id = 2
            elif body_message == "3":
                place_id = 3
            elif body_message == "4":
                place_id = 4

            place = PlaceTrigalUser.objects.get(id=place_id)
            user.place_to_work = place
            user.state = "work-end"
            user.save()
            return (
                "Haz escogido tu sede 🏠✅. \n\n"
                "Escoge el tipo de oferta laboral disponible: \n\n"
                "1️⃣ Campo 🌿 \n"
                "2️⃣ Poscosecha 💐 \n"
                "3️⃣ Otro 💼 \n"
            )
        else:
            return (
                "Opcion No valida. Recuerda selecionar el numero de la oferta laboral disponible \n\n"
            )

    elif user.state == "work-type":
        if body_message in ["1", "2", "3"]:
            if body_message == "1":
                type_work = "Campo"   
                user.work_type = type_work
                user.state = "work-document"
                user.save()
                return (
                "Haz escogido tu tipo de oferta laboral 🌿✅. \n\n"
                "Por favor escribe tu cédula en un solo mensaje 🪪.\n\n"
                )
            elif body_message == "2":
                type_work = "Poscosecha"
                user.work_type = type_work
                user.state = "work-document"
                return (
                "Haz escogido tu tipo de oferta laboral 🌿✅. \n\n"
                "Por favor escribe tu cédula en un solo mensaje 🪪.\n\n"
                )
            elif body_message == "3":
                user.state = "work-type-other"
                user.save()
                return(
                    "Escribe a cual tipo de trabajo deseas aplicar. \n"
                    "Trata de ser lo mas breve posible. \n"
                    "*Posibles ofertas* : \n\n"
                    "*Practicante* \n"
                    "*Administrativo* \n"
                )
        else:
            return (
                "Opcion No valida. Recuerda selecionar el numero de la oferta laboral disponible \n\n"
            )
        
    elif user.state == "work-type-other":
        user.work_type = body_message
        user.state = "work-document"
        user.save()
        return (
            "Haz escogido tu tipo de oferta laboral 🌿✅. \n\n"
            "Por favor escribe tu cédula en un solo mensaje 🪪.\n\n"
            )
    
    elif user.state == "work-type-other-two":
        user.work_type = body_message
        user.state = "En revision"
        user.number_attempts += 1
        user.save()
        return (
                    "Haz escogido tu tipo de oferta laboral 🌿✅. \n\n"
                    "Tu postulación ha sido completada satisfactoriamente y tu archvio se cargo en el sitema 📄💼. \n\n"
                    "Recuerda que puedes comunicarte con nosotros en cualquier momento escribiendo *Hola* 🌻😊.\n\n"
                    "Gracias por comunicarte con Flores El Trigal 🌸. \n\n"
                )

    elif user.state == "work-document":
        if body_message.isdigit():
            user.document = body_message
            user.state = "work-name"
            user.save()
            return (
                "Documento registrado exitosamente 🪪✅. \n\n"
                "*Por favor escribe tu nombre completo en un solo mensaje ✍🏻.*"
            )
        else:
            return (
                "El documento debe ser un numero sin espacios, sin puntos ni comas. \n"
                "Por favor escribe tu cédula en un solo mensaje 🪪.\n\n"
            )
    
    elif user.state == "work-name":
        if body_message.strip():
            user.name = body_message
            user.state = "work-experience"
            user.save()
            return (
                "Tu nombre ha sido registrado exitosamente ✅. \n\n"
                "Si cuentas con experiencia laboral, escribe *Si* \n\n"
                "En caso de *NO* tener experiencia laboral, escribe *No* \n\n"
            )

        
    elif user.state == "work-experience":
        if body_message.strip() == "NO" or body_message.strip() == "no" or body_message.strip() == "No" or body_message.strip() == "nO":
            user.experience = "El usuario ha seleccionado que no cuenta con experiencia laboral"
            user.state = "work-municipality"
            user.save()
            return (
                "Anotado exitosamente 📝. \n\n"
                "Por favor escribe tu municipio y departamento en un solo mensaje 🏠. \n"
            )

        elif body_message.strip() == "SI" or body_message.strip() == "si" or body_message.strip() == "Si" or body_message.strip() == "sI" or body_message.strip() == "sí" or body_message.strip() == "Sí" or body_message.strip() == "SÍ":
            user.state = "work-experience-text"
            user.save()
            return (
                "Escribe tu experiencia laboral en un solo mensaje 📝.\n\n"
            )
        else:
            return (
                "Opcion No valida. Recuerda escribir *Si* o *No* de acuerdo a tu experiencia laboral \n\n"
            )


    elif user.state == "work-experience-text" :
        if body_message.strip():
            user.experience = body_message
            user.state = "work-municipality"
            user.save()
            return (
                "Experiencia laboral registrada exitosamente 📝✅. \n\n"
                "Por favor escribe tu municipio y departamento en un solo mensaje 🏠. \n"
            )

    elif user.state == "work-municipality" :
        if body_message.strip():
            user.municipality = body_message
            user.state = "work-address"
            user.save()
            return (
                "Se registro correctamente 🏠✅. \n\n"
                "Por favor escribe tu dirección domiciliaria en un solo mensaje 🏠. \n"
            )
        else:
            return (
                "Opcion No valida. Recuerda escribir tu municipio o departamento \n\n"
            )

    elif user.state == "work-address" :
        if body_message.strip():
            user.address = body_message 
            user.state = "work-cv"
            user.save()
            return (
                "Dirección domiciliaria registrada exitosamente 🏠✅. \n\n"
                "*Si deseas agrega tu Hoja de vida📄💼 (Súbela a este chat)*, o escribre *finalizar* para continuar."
            )

    elif user.state == "work-end":
        if body_message in ["1", "2", "3"]:
            if body_message == "1":
                type_work = "Campo"
                user.state = "En revision"
                user.number_attempts += 1
                user.save()
                return (
                    "Haz escogido tu tipo de oferta laboral 🌿✅. \n\n"
                    "Tu postulación ha sido completada satisfactoriamente y tu archvio se cargo en el sitema 📄💼. \n\n"
                    "Recuerda que puedes comunicarte con nosotros en cualquier momento escribiendo *Hola* 🌻😊.\n\n"
                    "Gracias por comunicarte con Flores El Trigal 🌸. \n\n"
                )
            elif body_message == "2":
                user.state = "En revision"
                user.number_attempts += 1
                user.save()
                type_work = "Poscosecha"
                return (
                    "Haz escogido tu tipo de oferta laboral 🌿✅. \n\n"
                    "Tu postulación ha sido completada satisfactoriamente y tu archvio se cargo en el sitema 📄💼. \n\n"
                    "Recuerda que puedes comunicarte con nosotros en cualquier momento escribiendo *Hola* 🌻😊.\n\n"
                    "Gracias por comunicarte con Flores El Trigal 🌸. \n\n"
                )
            elif body_message == "3":
                user.state = "work-type-other-two"
                user.save()
                return(
                    "Escribe a cual tipo de trabajo deseas aplicar. \n"
                    "Trata de ser lo mas breve posible. \n"
                    "*Posibles ofertas* : \n\n"
                    "*Practicante* \n"
                    "*Administrativo* \n"
                )
        else:
            return (
                "Opcion No valida. Recuerda selecionar el numero de la oferta laboral disponible \n\n"
            )
        
    elif user.state == "En revision":
        return(
            "Tu postulación y tus datos ya estan a disposición de nuestro equipo de seleccón \n\n"
            "*Recuerda que puedes resolver dudas o preguntas, escribiendo inicio y luego digitando la opción 2*\n"
        )
            

    elif user.state == "work-cv":
        if body_message.lower() == "finalizar" :
            print("finalizar")
            user.state = "En revision"
            user.number_attempts += 1
            user.save()
            return (
                "Gracias por tu tiempo. \n\n"
                "Tu postulación ha sido completada satisfactoriamente. Te recomendamos estar pendiente del teléfono, te notificaremos lo antes posible. \n\n"
                "Recuerda que puedes comunicarte con nosotros en cualquier momento escribiendo *Hola* 🌻😊.\n\n"
                "Gracias por comunicarte con Flores El Trigal 🌸. \n\n"
            )
        elif media_url:
            print("media_url cv")
            success, message = save_files_applicants_function(media_type, media_url, user, profile_name)
            if success:
                print("success")
                user.state = "En revision"
                user.number_attempts += 1
                user.save()
                return (
                        "Gracias por tu tiempo. \n\n"
                        "Tu postulación ha sido completada satisfactoriamente y tu archvio se cargo en el sitema 📄💼. \n\n"
                        "Recuerda que puedes comunicarte con nosotros en cualquier momento escribiendo *Hola* 🌻😊.\n\n"
                        "Gracias por comunicarte con Flores El Trigal 🌸. \n\n"
                    )
            else:
                return(
                    "Lo siento, no es un archivo valido ☹️. \n\n"
                    "El sistema no reconocio tu archivo como una hoja de vida valida. Intenta de nuevo con otro archivo."
                )
        else: 
            return "*Opción NO válida ❌.* Por favor envía tu hoja de vida por este chat📄💼 o escribe 'finalizar' para continuar."

    elif user.state == "ask":
        if body_message.strip():
            if not body_message or not isinstance(body_message, str):
                return "Por favor escribe una pregunta valida 📝.\n\n"
            else:
                user.state = "En asesoria"
                user.save()
                response = billy_asesor_function(body_message)
                return response


def send_marketing_message_function(message_approved, placeName):
    """
    @brief Envía un mensaje de WhatsApp usando la API de Twilio.

    @param message_approved Mensaje de texto a enviar (contenido del mensaje aprobado o no aprobado).
    @param placeName Nombre del lugar desde donde se envía el mensaje.

    @return SID del mensaje enviado si tiene éxito. 
            Si ocurre un error, retorna un HttpResponse con el mensaje de error.
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=f"{message_approved} \n\nEste mensaje fue enviado por la sede {str(placeName)}",
            to='whatsapp:+573158062508'
        )
        print(message.sid)
        print("se envio el mensaje")
        return message.sid
    except Exception as e:
        print("Error al enviar mensaje:", str(e))
        return HttpResponse("Ha ocurrido un error: " + str(e))


def approved(request):
    """
    @brief Maneja la aprobación de un postulante y envía un mensaje personalizado según el estado.

    @param request Objeto HTTP que contiene los datos del postulante en formato JSON:
        {
            "place": {"id": ..., "name_place_trigal": ...},
            "approved": true|false
        }

    @return HttpResponse con un mensaje de éxito según si fue aprobado o no.
    """
    print(request.body)
    response = json.loads(request.body)
    place = response["place"]["id"]
    placeName = response["place"]["name_place_trigal"]

    if response["approved"] is True:
        message_approved = MessageTemplate.objects.filter(title="Mensaje Aprobados", place=place).first()
        print("Mensaje:", message_approved.description)
        print("Sede:", place)
        send_marketing_message_function(message_approved.description, placeName)
        return HttpResponse("Postulante aprobado correctamente")
    else:
        message_approved = MessageTemplate.objects.filter(title="Mensaje No Aprobados", place=place).first()
        print("Mensaje:", message_approved.description)
        print("Sede:", place)
        send_marketing_message_function(message_approved.description, placeName)
        return HttpResponse("Postulante no aprobado correctamente")


def send_marketing_message(request):
    """
    @brief Envía un mensaje de WhatsApp a todos los números válidos listados en un archivo Excel cargado.

    @details El Excel debe tener una columna llamada "Celulares" con números iniciando por '57'.
             Se ignoran números mal formateados y se devuelve un resumen de enviados y fallidos.

    @param request Objeto HTTP con un JSON que contiene:
        {
            "message": "Contenido del mensaje",
            "place": "Nombre del lugar"
        }

    @return JsonResponse con los números a los que se envió y los que fallaron, o un error.
    """
    try:
        data = json.loads(request.body)
        message_to_send = data.get("message")
        place_name = data.get("place")

        if not message_to_send or not place_name:
            return JsonResponse({"error": "Faltan campos 'message' o 'place'."}, status=400)

        place = PlaceTrigalUser.objects.get(name_place_trigal=place_name)
        excel = UploadExcelFile.objects.get(place=place.id)
        excel_path_file = excel.file.path
        df = pd.read_excel(excel_path_file)

        if "Celulares" not in df.columns:
            return JsonResponse({"error": "La columna 'Celulares' no existe en el Excel cargado."}, status=400)

        phone_numbers = df["Celulares"].dropna().astype(str)
        phone_numbers_condition = phone_numbers[phone_numbers.str.startswith('57')]

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        send_to = []
        failed_numbers = []

        for number_to_send in phone_numbers_condition:
            try:
                client.messages.create(
                    body=message_to_send,
                    from_=f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
                    to=f"whatsapp:+{number_to_send}"
                )
                send_to.append(number_to_send)
            except Exception as e:
                failed_numbers.append({"number": number_to_send, "error": str(e)})

        return JsonResponse({
            "success": True,
            "sent_numbers": send_to,
            "failed_numbers": failed_numbers
        })

    except PlaceTrigalUser.DoesNotExist:
        return JsonResponse({"error": "No se encontró el lugar especificado."}, status=404)
    except UploadExcelFile.DoesNotExist:
        return JsonResponse({"error": "No se encontró el archivo Excel para ese lugar."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)

