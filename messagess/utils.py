import os
import requests
from django.conf import settings
import re
from pdf2image import convert_from_path
import tempfile
import logging
from io import BytesIO
from google import genai
from google.genai import types
import pdfplumber
import json
from PIL import Image
from spire.doc import *
from spire.doc.common import *

"""
    save_files_applicants_function:

    funcion de utilidad para guardar lo archivos que suba un usuario
"""

logger = logging.getLogger(__name__)

def save_files_applicants_function(media_type, media_url, user, profile_name):
    response_media = requests.get(media_url, auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN))

    if response_media.status_code == 200 and len(response_media.content) > 0:
        safe_file = re.sub(r"[^\w\-]", "-", f"{profile_name}_{user.phone_number}")

        if media_type == "application/pdf":
            ext = "pdf"
        elif media_type.startswith("image/"):
            ext = media_type.split("/")[-1]
            if ext == "jpeg":
                ext = "jpg"
        elif media_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            ext = "docx"
        else:
            ext = "bin"

        file_name = f"{safe_file}.{ext}"

        # Carpeta de destino: media/whatsapp/
        folder = "whatsapp"
        relative_path = os.path.join(folder, file_name)  # whatsapp/nombre.pdf
        file_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(response_media.content)

        user.cv.name = relative_path
        user.save()

        success_message = "Tu documento se ha guardado exitosamente \n\n"
        return True, success_message
    else:
        return False


"""
    is_scanned_pdf_function

    Valida si un archivo PDF es escaneado o si es texto
    Devuelve True si es escaneado, False si no lo es.
    Si contiene texto se le pasa crudo a google generative ai
    Si es escaneado se convierte en imagenes para ser analizado.
"""


def is_scanned_pdf_function(file_path):
    try:
        with pdfplumber.open(file_path) as pdf_file:
            pages = pdf_file.pages
            long = len(pages)
            for page in pages:
                text = page.extract_text()
                if text and len(text.strip()) > 50:
                    return False
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
    return True


"""
    json_convert_data_function:

    Convierte los datos del JSON en un diccionario de python
    Guarda los datos del diccionario en el modelo de datos de la base de datos
    Devuelve True si se guardo correctamente, False para caso contrario

"""

def json_convert_data_function(json_data, user):
    json_data = json.loads(json_data)
    try:
        user.name = json_data["Nombre Completo"].lower()
        user.document = json_data["Documento"]
        user.experience = json_data["Experiencia"].lower()
        user.address = json_data["Direccion Domiciliaria"].lower()
        user.work_type = json_data["Tipo de Trabajo"]
        user.save()
        return True
    except Exception as e:
        logger.error(f"Error processing JSON: {str(e)}", exc_info=True)
        return False


"""
    Valida si un archivo PDF es una hoja de vida usando Google Generative AI.
    Acepta PDF, Word e imagenes. Pdf y word se convierten en imagenes para ser analizados.
    Si el PDF es una imagen, usa OCR para extraer el texto.
    Devuelve True si es una hoja de vida, False si no lo es.
"""

def ai_validator_file_function(body_message, media_type, media_url, user):
    try:
        response_media = requests.get(
            media_url,
            auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            timeout=10
        )
        response_media.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error downloading media: {e}", exc_info=True)
        return False


    file_content = BytesIO(response_media.content)
    client = genai.Client(api_key=settings.API_KEY_GEMINI)

    role = (
                "Eres un asistente que analiza el contenido de un archivo para determinar si es una hoja de vida. "
                "Si el archivo contiene información personal como nombre, experiencia laboral, educación o habilidades, "
                "devuelve únicamente un objeto JSON crudo, sin ningún texto adicional, sin etiquetas de Markdown como ```json o ```, "
                "sin espacios ni líneas extras, con las claves: 'Nombre Completo', 'Documento', 'Experiencia', 'Direccion Domiciliaria' , 'Tipo de Trabajo'"
                "El valor de la clave 'Documento' debe ir sin puntos, comas, guiones o cualquier caracter especial. Unicamente numeros"
                "El valor de la clave 'Tipo de Trabajo' debe de ser Campo o Poscosecha, (relacionado con trabajo en Flores) en caso de que no se encuentre 'No especificado'"
                "Si alguno de estos datos no se encuentra, su valor será 'No especificado'. "
                "Si NO es una hoja de vida o no se puede extraer información, responde únicamente con la palabra 'False' (sin comillas, como texto plano). "
                "IMPORTANTE: No uses Markdown, no envuelvas la respuesta en ```json ni en ningún otro formato."
            )

    context = [role]

    # IMAGEN
    if media_type.startswith("image/"):
        with Image.open(file_content) as image:
            image_format = image.format if image.format in ["JPEG", "PNG", "GIF", "BMP", "TIFF"] else "JPEG"
            suffix = '.jpg' if image_format == 'JPEG' else '.png'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_image:
                image.save(temp_image, format=image_format)
                temp_image_path = temp_image.name
                my_file = client.files.upload(file=f"{temp_image_path}")

                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents= [context, my_file]
                )

                client.files.delete(name=my_file.name)

                if response.text != "False":
                    try:
                        json_response = json_convert_data_function(response.text, user)
                        if json_response == True:
                            return "True"
                        else:
                            return "False"
                    except json.JSONDecodeError as e:
                        logger.error(f"Error processing JSON: {str(e)}", exc_info=True)
                    except Exception as e:
                        logger.error(f"Error processing JSON: {str(e)}", exc_info=True)
                else:
                    return "False"

    # PDF 
    elif media_type == "application/pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf.write(file_content.getvalue())
                temp_pdf_path = temp_pdf.name 
                my_file = client.files.upload(file=f"{temp_pdf_path}")

                if is_scanned_pdf_function(temp_pdf_path):
                    images = convert_from_path(temp_pdf_path, dpi=300, poppler_path=r"C:\poppler\poppler-24.08.0\Library\bin")
                    for i, image in enumerate(images):
                        context.append(image)
                    
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents= [context, my_file]
                    )

                    client.files.delete(name=my_file.name)

                    if response.text != "False":
                        try:
                            json_response = json_convert_data_function(response.text, user)
                            if json_response == True:
                                return "True"
                            else:
                                return "False"
                        except json.JSONDecodeError as e:
                            logger.error(f"Error processing JSON: {str(e)}", exc_info=True)
                        except Exception as e:
                            logger.error(f"Error processing JSON: {str(e)}", exc_info=True)
                    else:
                        return "False"

                else:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents= [context, my_file]
                    )

                    client.files.delete(name=my_file.name)

                    if response.text != "False":
                        try:
                            json_response = json_convert_data_function(response.text, user)
                            if json_response == True:
                                return "True"
                            else:
                                return "False"
                        except json.JSONDecodeError as e:
                            logger.error(f"Error processing JSON: {str(e)}", exc_info=True)
                        except Exception as e:
                            logger.error(f"Error processing JSON: {str(e)}", exc_info=True)
                    else:
                        return "False"

    # WORD
    elif media_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
            temp_docx.write(file_content.getvalue())
            temp_docx_path = temp_docx.name 

        temp_word_to_pdf_path = os.path.splitext(temp_docx_path)[0] + ".pdf"

        document = Document()
        document.LoadFromFile(temp_docx_path)
        document.SaveToFile(temp_word_to_pdf_path, FileFormat.PDF)

        print(f"Archivo convertido a PDF: {temp_word_to_pdf_path}") 

        my_file = client.files.upload(file=f"{temp_word_to_pdf_path}")
            
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents= [context, my_file]
        )

        client.files.delete(name=my_file.name)
        document.Close()

        try:
            if os.path.exists(temp_docx_path):
                os.remove(temp_docx_path)
            if os.path.exists(temp_word_to_pdf_path):
                os.remove(temp_word_to_pdf_path)
            else:
                logger.info("Nada para eliminar")
        except Exception as e:
            logger.error(f"Error removing temporary file: {str(e)}", exc_info=True)
        finally:
            print("Cerrando documento")

        if response.text != "False":
            try:
                json_response = json_convert_data_function(response.text, user)
                if json_response == True:
                    return "True"
                else:
                    return "False"
            except json.JSONDecodeError as e:
                logger.error(f"Error processing JSON: {str(e)}", exc_info=True)
            except Exception as e:
                logger.error(f"Error processing JSON: {str(e)}", exc_info=True)
        else:
            return "False"




