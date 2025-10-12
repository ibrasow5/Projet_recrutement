# recrutement/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('recruteur', 'Recruteur'),
        ('candidat', 'Candidat'),
    ]
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidat')

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def get_full_name(self):
        """Retourne le prénom et nom complet"""
        return f"{self.prenom} {self.nom}".strip()

    def __str__(self):
        return self.get_full_name() or self.username


class Candidat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    cv = models.FileField(upload_to='cv/', null=True, blank=True)
    offre = models.ForeignKey('OffreEmploi', on_delete=models.SET_NULL, null=True, blank=True, related_name="candidats")

    def __str__(self):
        if self.user:
            return self.user.get_full_name()
        return "Candidat sans utilisateur"


class OffreEmploi(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    date_publication = models.DateField(auto_now_add=True)
    date_limite = models.DateField()

    def __str__(self):
        return self.titre