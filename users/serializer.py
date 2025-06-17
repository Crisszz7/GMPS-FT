# Un serializer transforma objetos Python a formatos JSON que se usan en APIs

from rest_framework import serializers
from .models import PlaceTrigalUser, WhatsappUser, AdministerUser, UserHistory, UserReject

# Serializer para el modelo PlaceTrigalUser
class PlaceTrigalSerializer(serializers.ModelSerializer):
    """
    @class PlaceTrigalSerializer
    @brief Serializer para convertir objetos PlaceTrigalUser en formato JSON.
    """

    class Meta:
        model = PlaceTrigalUser
        fields = ['id', 'name_place_trigal']


# Serializer para el modelo WhatsappUser
class WhatsappUserSerializer(serializers.ModelSerializer):
    """
    @class WhatsappUserSerializer
    @brief Serializer para el modelo WhatsappUser. Incluye formateo de fecha y campo adicional para la URL completa del CV.
    """
    date_request = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)
    cv_full_url = serializers.SerializerMethodField()

    class Meta:
        model = WhatsappUser
        fields = '__all__'
        depth = 1

    def get_cv_full_url(self, obj):
        """
        @brief Genera la URL absoluta del archivo CV asociado al usuario.
        @param obj: Instancia del modelo WhatsappUser.
        @return URL absoluta para descarga del CV si existe, o None.
        """
        request = self.context.get("request")
        if obj.cv:
            return request.build_absolute_uri(f"/api/users/download-cv/{obj.id}/")
        return None


# Serializer para el modelo AdministerUser
class AdministerUserSerializer(serializers.ModelSerializer):
    """
    @class AdministerUserSerializer
    @brief Serializer para el modelo AdministerUser. Incluye lógica personalizada para creación con hash de contraseña.
    """

    class Meta:
        model = AdministerUser
        fields = ['id', 'username', 'email', 'password', 'place_to_administer']
        extra_kwargs = {'password': {'write_only': True}}  # Evita que el password se muestre en la respuesta

    def create(self, validated_data):
        """
        @brief Crea una instancia de AdministerUser hasheando la contraseña antes de guardarla.
        @param validated_data: Datos validados del usuario.
        @return Instancia del usuario creada.
        """
        password = validated_data.pop('password')  # Extrae y elimina la contraseña original
        user = AdministerUser(**validated_data)
        user.set_password(password)  # Hashea la contraseña
        user.save()
        return user


# Serializer para el modelo UserHistory
class UserHistorySerializer(serializers.ModelSerializer):
    """
    @class UserHistorySerializer
    @brief Serializer para el modelo UserHistory. Muestra fecha formateada y si el usuario fue aprobado.
    """
    date = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)
    approved = serializers.BooleanField(source='user.approved', read_only=True)

    class Meta:
        model = UserHistory
        fields = ['id', 'user', 'comments', 'date', 'approved']
        depth = 1


# Serializer para el modelo UserReject
class UserRejectSerializer(serializers.ModelSerializer):
    """
    @class UserRejectSerializer
    @brief Serializer para el modelo UserReject. Serializa todos los campos.
    """

    class Meta:
        model = UserReject
        fields = '__all__'
