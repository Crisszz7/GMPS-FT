from rest_framework import serializers
from .models import MessageAiUser, MessageTemplate, UploadExcelFile

# Serializer para el modelo MessageAiUser
class MessageAiSerializer(serializers.ModelSerializer):
    """
    @class MessageAiSerializer
    @brief Serializer para los mensajes entre la IA y el usuario.
    """
    class Meta: 
        model = MessageAiUser
        fields = ['id', 'ask', 'answer']


# Serializer para el modelo MessageTemplate
class MessageTemplateSerializer(serializers.ModelSerializer):
    """
    @class MessageTemplateSerializer
    @brief Serializer para los mensajes reiterativos de marketing asignados a un lugar (place).
    """
    class Meta:
        model = MessageTemplate
        fields = ['id', 'title', 'description', 'place']


# Serializer para el modelo UploadExcelFile
class UploadExcelFileSerializer(serializers.ModelSerializer):
    """
    @class UploadExcelFileSerializer
    @brief Serializer para la carga de archivos Excel. Expone columnas y datos al cliente.
    """
    columns = serializers.SerializerMethodField()  # Campo personalizado para devolver columnas del archivo
    data = serializers.SerializerMethodField()     # Campo personalizado para devolver contenido del archivo

    class Meta:
        model = UploadExcelFile
        fields = ['id', 'file', 'place', 'columns', 'data']

    def create(self, validated_data):
        """
        @brief Asigna automáticamente el lugar (place) según el usuario autenticado al subir el archivo.
        @param validated_data: Datos validados del archivo.
        @return Instancia creada del modelo UploadExcelFile.
        """
        request = self.context.get("request")
        user = request.user
        validated_data['place'] = user.place_to_administer
        return super().create(validated_data)

    def get_columns(self, obj):
        """
        @brief Obtiene las columnas del archivo Excel subido.
        @param obj: Instancia del modelo UploadExcelFile.
        @return Lista de nombres de columnas (o mensaje de error).
        """
        return obj.get_columns()

    def get_data(self, obj):
        """
        @brief Obtiene los datos del archivo Excel como lista de diccionarios.
        @param obj: Instancia del modelo UploadExcelFile.
        @return Contenido del archivo como JSON (o mensaje de error).
        """
        return obj.get_data()
