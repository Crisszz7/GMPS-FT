from rest_framework import serializers
from .models import MessageAiUser, MessageTemplate, UploadExcelFile


class MessageAiSerializer(serializers.ModelSerializer):
    class Meta: 
        model = MessageAiUser
        fields = ['id', 'ask' , 'answer']


class MessageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTemplate
        fields = ['id',  'title', 'description', 'place']


class UploadExcelFileSerializer(serializers.ModelSerializer):
    columns = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()

    class Meta:
        model = UploadExcelFile
        fields = ['id', 'file', 'place' , 'columns' , 'data']

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        validated_data['place'] = user.place_to_administer
        return super().create(validated_data)

    def get_columns(self, obj):
        return obj.get_columns()

    def get_data(self, obj):
        return obj.get_data()




