# recrutement/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('recruteur', 'Recruteur'),
        ('candidat', 'Candidat'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidat')

    def __str__(self):
        return self.username

class Candidat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    cv = models.FileField(upload_to='cv/', null=True, blank=True)
    offre = models.ForeignKey('OffreEmploi', on_delete=models.SET_NULL, null=True, blank=True, related_name="candidats")

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

class OffreEmploi(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    date_publication = models.DateField(auto_now_add=True)
    date_limite = models.DateField()

    def __str__(self):
        return self.titre        

