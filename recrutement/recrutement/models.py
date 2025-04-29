# recrutement/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('recruteur', 'Recruteur'),
        ('candidat', 'Candidat'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidat')

    def __str__(self):
        return self.username

class Candidat(models.Model):
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    cv = models.FileField(upload_to='cv/', null=True, blank=True)
    date_naissance = models.DateField()
    telephone = models.CharField(max_length=15, default='0000000000')

    def __str__(self):
        return f'{self.prenom} {self.nom}'
