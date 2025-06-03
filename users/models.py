from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

#Modelo para las sedes 
class PlaceTrigalUser(models.Model):
    name_place_trigal =  models.CharField(max_length=30)

    def __str__(self):
        return self.name_place_trigal

class AdministerUser(AbstractUser):
    email = models.EmailField(max_length=70, blank=False, null=False)
    place_to_administer = models.ForeignKey(PlaceTrigalUser, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str( self.place_to_administer)



#Modelo para los usuarios que se comunican mediante Whatsapp
class WhatsappUser(models.Model):
    phone_number = models.CharField(max_length=25, unique=True)
    name = models.CharField(max_length=50, null=True)
    document = models.CharField(max_length=30, unique=True, null=True)
    work_type = models.CharField(max_length=40, null=True, blank=True)
    experience = models.TextField(blank=True)
    address = models.TextField()
    cv = models.FileField(upload_to='whatsapp', null=True, blank=True)
    state = models.CharField(max_length=40, blank=True, null=True)
    date_request = models.DateTimeField(auto_now_add=True)
    place_to_work = models.ForeignKey("users.PlaceTrigalUser", on_delete=models.CASCADE, null=True)



    def __str__(self):
        return(
            str(self.phone_number) + "-" +
            str(self.name) + "-" +
            str(self.document) + "-" +
            str(self.experience) + "-" +
            str(self.address) + "-" + 
            str(self.cv) + "-" +
            str(self.state) + "-" +
            str(self.date_request) + "-" +
            str(self.place_to_work)
            )
    
    
#Modelo para los administradores


