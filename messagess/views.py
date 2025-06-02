from typing import override
from twilio.rest import Client
from twilio.twiml.messaging_response import Message , MessagingResponse
from rest_framework import viewsets
from .models import MessageAiUser, MessageTemplate, PlaceTrigalUser, UploadExcelFile
from users.models import WhatsappUser
from .serializer import MessageAiSerializer, MessageTemplateSerializer, UploadExcelFileSerializer
from django.conf import settings
from django.http import HttpResponse
from twilio.request_validator import RequestValidator
import logging
from .utils import save_files_applicants_function, ai_validator_file_function
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Create your views here.
class MessageAiViewSet(viewsets.ModelViewSet):
    queryset = MessageAiUser.objects.all()
    serializer_class = MessageAiSerializer

class UploadExcelFileViewSet(viewsets.ModelViewSet):
    queryset = UploadExcelFile.objects.all()
    serializer_class = UploadExcelFileSerializer

    def get_queryset(self):
        user = self.request.user
        user_place_id = user.place_to_administer.id
        return UploadExcelFile.objects.filter(place=user_place_id)
        

class MessageTemplateViewSet(viewsets.ModelViewSet):
    queryset = MessageTemplate.objects.all()
    serializer_class = MessageTemplateSerializer

    def get_queryset(self):
        user = self.request.user
        user_place_id = user.place_to_administer.id
        return MessageTemplate.objects.filter(place=user_place_id) 
    
    # es un método especial de Django REST Framework que se ejecuta automáticamente 
    # cuando haces un POST a un ModelViewSet.
    def perform_create(self, serializer):
        user = self.request.user # obtener el usuario que hace la petición 
        serializer.save(place=user.place_to_administer) # guarda en la bd y le asigna el avlor a place 

#funcion para hablar con billy asesor

def billy_asesor_function(body_message):

    list_messages = MessageAiUser.objects.all().values_list('ask', 'answer')

    messages = "\n\n" .join([f"[{i+1}] Respuesta:{answer} \n Pregunta:{ask} \n\n " for i, (ask, answer) in enumerate(list_messages)])
    print(messages)

    context = f"Listado de preguntas: {messages}\n\nUsuario pregunta:{body_message}" 

    client = genai.Client(api_key=settings.API_KEY_GEMINI)

    try:
        response = client.models.generate_content(
            model= "gemini-2.0-flash",
            config = types.GenerateContentConfig(
                system_instruction="Eres un asistente que responde basado en un listado de preguntas y respuestas. Dara una respuesta que coincida o se asemeje. Si la pregunta no coincide con ninguna del listado, di: 'Para una pregunta detallada, un asesor te contactará (horario: 6:00 am - 2:30 pm)'.",
                temperature=0.3,
                max_output_tokens=200,
            ),
            contents = context
        )

        return response.text

    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}", exc_info=True)
        return "Un error ha ocurrido, intenta esta opción mas tarde."


    

#funciones para el manejo de los mensajes

"""
    webhook_twilio_whatsapp_function: 

    Maneja la entrada del usuario cuando llega un nuevo mensaje
    Recoge los datos del remitente (Numero del remitente(From), Cuerpo del mensaje(body))
    Pasa los datos a la función responsable de crear los mensajes
""" 


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
        response.message("Un error ha ocurrido, intenta esta opción mas tarde")
        return HttpResponse(str(response), content_type="text/xml") # retorna la respuesta en marcado TwiML (lenguaje de Hypertxto de twilio )


"""
    send_message_whatsapp_function: 

    Funcion encargada de crear los mensajes que se envian en formato TwiML
    Recibe el cuerpo del mensaje, el usuario y si este ha envido contenido Media, pasados desde el webhook
    Llama a la funcion que procesa los mensajes y le pasa los parametros necesarios 
    Procesa la respuesta que llega de la funcion "process_user_input_function" y envia el mensaje al webhook
""" 

def send_message_whatsapp_function(body_message, user,  media_type, media_url, profile_name):

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
                            "Si deseas volver al menu principal escribe inicio en cualquier momento"
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
            )
        else:
            return (
                "Opcion No valida. Recuerda selecionar el numero de la oferta laboral disponible \n\n"
            )

    elif user.state == "work-place-cv" and user.work_type == "Dato no encontrado -IA":
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
            )
        else:
            return (
                "Opcion No valida. Recuerda selecionar el numero de la oferta laboral disponible \n\n"
            )

    elif user.state == "work-type":
        if body_message in ["1", "2"]:
            if body_message == "1":
                type_work = "Campo"
            elif body_message == "2":
                type_work = "Poscosecha"

            user.work_type = type_work
            user.state = "work-document"
            user.save()
            return (
                "Haz escogido tu tipo de oferta laboral 🌿✅. \n\n"
                "Por favor escribe tu cédula en un solo mensaje 🪪.\n\n"
            )
        else:
            return (
                "Opcion No valida. Recuerda selecionar el numero de la oferta laboral disponible \n\n"
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
            user.state = "work-address"
            user.save()
            return (
                "Anotado exitosamente 📝. \n\n"
                "Por favor escribe tu dirección en un solo mensaje 🏠. \n"
                "*Debes incluir la ciudad/municipio y el departamento* \n\n"
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
            user.state = "work-address"
            user.save()
            return (
                "Experiencia laboral registrada exitosamente 📝✅. \n\n"
                "Por favor escribe tu dirección en un solo mensaje 🏠. \n"
                "*Debes incluir la ciudad/municipio y el departamento* \n\n"
            )

    elif user.state == "work-address" :
        if body_message.strip():
            user.address = body_message
            user.state = "work-cv"
            user.save()
            return (
                "Dirección registrada exitosamente 🏠✅. \n\n"
                "*Si deseas agrega tu Hoja de vida📄💼 (Súbela a este chat)*, o escribre *finalizar* para continuar."
            )

    elif user.state == "work-end":
        if body_message in ["1", "2"]:
            if body_message == "1":
                type_work = "Campo"
            elif body_message == "2":
                type_work = "Poscosecha"
            user.work_type = type_work
            user.state = "En revision"
            user.save()
            return (
                "Haz escogido tu tipo de oferta laboral 🌿✅. \n\n"
                "Tu postulación ha sido completada satisfactoriamente y tu archvio se cargo en el sitema 📄💼. \n\n"
                "Recuerda que puedes comunicarte con nosotros en cualquier momento escribiendo *Hola* 🌻😊.\n\n"
                "Gracias por comunicarte con Flores El Trigal 🌸. \n\n"
            )
        else:
            return (
                "Opcion No valida. Recuerda selecionar el numero de la oferta laboral disponible \n\n"
            )

    elif user.state == "work-cv":
        if body_message.lower() == "finalizar" :
            print("finalizar")
            user.state = "En revision"
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








