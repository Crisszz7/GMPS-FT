from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo para las sedes
class PlaceTrigalUser(models.Model):
    """
    @class PlaceTrigalUser
    @brief Modelo para representar las diferentes sedes disponibles para los usuarios y administradores.
    """

    name_place_trigal = models.CharField(max_length=30)

    def __str__(self):
        """
        @brief Representación textual de la sede.
        @return Nombre de la sede como cadena de texto.
        """
        return self.name_place_trigal


# Modelo para los administradores
class AdministerUser(AbstractUser):
    """
    @class AdministerUser
    @brief Modelo de usuario personalizado que hereda de AbstractUser, con un campo adicional para la sede que administra.
    """

    email = models.EmailField(max_length=70, blank=False, null=False)
    place_to_administer = models.ForeignKey(PlaceTrigalUser, on_delete=models.CASCADE, null=True)

    def __str__(self):
        """
        @brief Representación textual del administrador.
        @return Nombre de la sede administrada como cadena de texto.
        """
        return str(self.place_to_administer)


# Modelo para los usuarios que se comunican mediante WhatsApp
class WhatsappUser(models.Model):
    """
    @class WhatsappUser
    @brief Modelo para almacenar los datos de usuarios que se postulan a través de WhatsApp.
    """

    phone_number = models.CharField(max_length=25, unique=True)
    name = models.CharField(max_length=200, null=True)
    document = models.CharField(max_length=30, null=True)
    work_type = models.CharField(max_length=40, null=True, blank=True, default="No especificado")
    municipality = models.CharField(max_length=60, null=True, blank=True)
    experience = models.TextField(blank=True)
    address = models.TextField()
    cv = models.FileField(upload_to='whatsapp', null=True, blank=True)
    state = models.CharField(max_length=40, blank=True, null=True)
    date_request = models.DateTimeField(auto_now_add=True)
    place_to_work = models.ForeignKey(PlaceTrigalUser, on_delete=models.CASCADE, null=True)
    approved = models.BooleanField(default=False)
    reject = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    number_attempts = models.IntegerField(default=0)

    def __str__(self):
        """
        @brief Representación textual del usuario de WhatsApp.
        @return Cadena con información básica del postulante.
        """
        return (
            str(self.phone_number) + " - " +
            str(self.name) + " - " +
            str(self.document) + " - " +
            str(self.work_type) + " - " +
            str(self.municipality) + " - " +
            str(self.experience) + " - " +
            str(self.address) + " - " +
            str(self.cv) + " - " +
            str(self.state) + " - " +
            str(self.date_request) + " - " +
            str(self.place_to_work) + " - " +
            str(self.approved) + " - " +
            str(self.archived)
        )


# Modelo para el historial de comentarios realizados por administradores sobre usuarios
class UserHistory(models.Model):
    """
    @class UserHistory
    @brief Modelo para guardar el historial de comentarios hechos por los administradores sobre un postulante.
    """

    user = models.ForeignKey(WhatsappUser, on_delete=models.CASCADE)
    comments = models.TextField(blank=True, default="Postulante archivado")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        @brief Representación textual del historial.
        @return Comentarios con fecha e identificador del usuario.
        """
        return (
            str(self.user) + " - " +
            str(self.comments) + " - " +
            str(self.date)
        )


# Modelo para usuarios rechazados
class UserReject(models.Model):
    """
    @class UserReject
    @brief Modelo para guardar la información básica de postulantes rechazados y su número de aplicaciones.
    """

    document = models.CharField(max_length=30, unique=True, null=False)
    name = models.CharField(max_length=200, null=False)
    place = models.ForeignKey(PlaceTrigalUser, on_delete=models.CASCADE)
    applications_to_job = models.IntegerField(blank=False, null=False, default=0)

    def __str__(self):
        """
        @brief Representación textual del usuario rechazado.
        @return Nombre y documento del usuario rechazado con la cantidad de postulaciones.
        """
        return f"{self.name} ({self.document}) - Postulaciones: {self.applications_to_job}"
