from django.db import models
import pandas as pd
import json

# Modelo para los mensajes de la IA al usuario
class MessageAiUser(models.Model):
    """
    @class MessageAiUser
    @brief Modelo para almacenar los mensajes enviados por la IA al usuario, incluyendo la pregunta y su respectiva respuesta.
    """

    ask = models.CharField(max_length=300)
    answer = models.TextField(blank=False, null=False, max_length=300)

    def __str__(self):
        """
        @brief Representación textual del mensaje.
        @return Pregunta y respuesta concatenadas en una sola cadena.
        """
        return self.ask + " " + self.answer


# Modelo para los mensajes reiterativos de marketing
class MessageTemplate(models.Model):
    """
    @class MessageTemplate
    @brief Modelo para almacenar plantillas de mensajes automatizados de marketing, asociadas a una sede.
    """

    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=False, null=False, default="...", max_length=2000)
    place = models.ForeignKey("users.PlaceTrigalUser", on_delete=models.CASCADE, null=True)

    def __str__(self):
        """
        @brief Representación textual de la plantilla de mensaje.
        @return Título, descripción y sede asociada en una sola cadena.
        """
        return self.title + " " + self.description + " " + str(self.place)


# Modelo para cargar y procesar archivos Excel
class UploadExcelFile(models.Model):
    """
    @class UploadExcelFile
    @brief Modelo para almacenar archivos Excel subidos, vinculados a una sede específica.
    También proporciona métodos para leer y procesar los datos del archivo.
    """

    file = models.FileField(upload_to="excel")
    place = models.ForeignKey("users.PlaceTrigalUser", on_delete=models.CASCADE, null=True)

    def get_columns(self):
        """
        @brief Extrae las columnas del archivo Excel subido.
        @return Una lista en formato JSON con los nombres de las columnas o un mensaje de error.
        """
        try:
            df = pd.read_excel(self.file.path)
            return json.dumps(list(df.columns))
        except Exception as e:
            return "Error processing Excel file: " + str(e)

    def get_data(self):
        """
        @brief Obtiene todos los datos del archivo Excel como una lista de diccionarios.
        @return Datos estructurados en formato dict (orient='records') o mensaje de error.
        """
        try:
            df = pd.read_excel(self.file.path)
            return df.to_dict(orient='records')
        except Exception as e:
            return "Error processing Excel file: " + str(e)
