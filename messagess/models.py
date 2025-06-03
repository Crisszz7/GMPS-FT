from django.db import models
import pandas as pd
import json

# Modelo para los mensajes de la IA al usuario 
class MessageAiUser(models.Model):
    ask = models.CharField(max_length=300)
    answer = models.TextField(blank=False ,null=False, max_length=300)

    def __str__(self):
        return self.ask + " " + self.answer

# Modelo para los mensajes reiterativos de Marketing
class MessageTemplate(models.Model):
    title = models.CharField(max_length=100, blank=False)
    description= models.TextField(blank=False, null=False, default="...", max_length=2000)
    place = models.ForeignKey("users.PlaceTrigalUser", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title + " " + self.description + " " + str(self.place)

# Modelo para cargar archivos Excel
class UploadExcelFile(models.Model):
    file = models.FileField(upload_to="excel")
    place = models.ForeignKey("users.PlaceTrigalUser", on_delete=models.CASCADE, null=True)

    def get_columns(self):
        try:
            df = pd.read_excel(self.file.path)
            return json.dumps(list(df.columns))
        except Exception as e:
            return "Error processing Excel file: " + str(e)

    def get_data(self):
        try:
            df = pd.read_excel(self.file.path)
            return df.to_dict(orient='records')
        except Exception as e:
            return "Error processing Excel file: " + str(e)
