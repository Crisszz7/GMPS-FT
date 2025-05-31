#un serializer transforma objetos (python) a fromatos Json que se usan en APIs

from rest_framework import serializers
from .models import PlaceTrigalUser, WhatsappUser, AdministerUser
from django.conf import settings


class PlaceTrigalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceTrigalUser
        fields = ['id' , 'name_place_trigal']


class WhatsappUserSerializer(serializers.ModelSerializer):
    date_request = serializers.DateTimeField(format="%d/%m/%Y %H:%M")
    cv_full_url = serializers.SerializerMethodField()

    class Meta:
        model = WhatsappUser
        fields ='__all__'

    def get_cv_full_url(self, obj):
        request = self.context.get("request")
        if obj.cv:
            # Construye la URL completa automáticamente desde el dominio actual
            return request.build_absolute_uri(f"/api/messages/media/{obj.cv.name}")
        return None
        
    



class AdministerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdministerUser
        fields = ['id', 'username', 'email', 'password', 'place_to_administer']
        extra_kwargs = {'password': {'write_only': True}} #evita que se muestre el password en la respuesta

    def create(self, validated_data):
        password = validated_data.pop('password') # extrae la contraseña del diccionario y la elimina del mismo para pasarla hasheada
        user = AdministerUser(**validated_data)
        user.set_password(password) # hashea la contraseña
        user.save()
        return user



