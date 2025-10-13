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
    TYPE_CONTRAT_CHOICES = [
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('Stage', 'Stage'),
        ('Alternance', 'Alternance'),
        ('Freelance', 'Freelance'),
    ]
    
    entreprise = models.CharField(max_length=255, verbose_name="Entreprise")
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, verbose_name="Logo entreprise")
    localisation = models.CharField(max_length=255, verbose_name="Localisation")
    titre = models.CharField(max_length=255, verbose_name="Titre du poste")
    description = models.TextField(verbose_name="Description")
    type_contrat = models.CharField(max_length=50, choices=TYPE_CONTRAT_CHOICES, default='CDI', verbose_name="Type de contrat")
    salaire_min = models.IntegerField(null=True, blank=True, verbose_name="Salaire minimum (FCFA)")
    salaire_max = models.IntegerField(null=True, blank=True, verbose_name="Salaire maximum (FCFA)")
    competences = models.TextField(help_text="Séparez les compétences par des virgules", verbose_name="Compétences requises")
    temps_plein = models.BooleanField(default=True, verbose_name="Temps plein")
    urgent = models.BooleanField(default=False, verbose_name="Offre urgente")
    nouveau = models.BooleanField(default=True, verbose_name="Nouvelle offre")
    date_publication = models.DateField(auto_now_add=True)
    date_limite = models.DateField(verbose_name="Date limite de candidature")
    nb_candidats = models.IntegerField(default=0, verbose_name="Nombre de candidats")

    def __str__(self):
        return f"{self.titre} - {self.entreprise}"
    
    def get_salaire_display(self):
        if self.salaire_min and self.salaire_max:
            # Fonction pour formater un montant
            def format_montant(montant):
                if montant >= 1_000_000:
                    # Millions
                    m = montant / 1_000_000
                    if m == int(m):
                        return f"{int(m)}M"
                    else:
                        return f"{m:.1f}M"
                else:
                    # Milliers
                    k = montant / 1_000
                    if k == int(k):
                        return f"{int(k)}K"
                    else:
                        return f"{k:.0f}K"
            
            return f"{format_montant(self.salaire_min)} - {format_montant(self.salaire_max)} FCFA"
        return "Non spécifié"
    
    def get_competences_list(self):
        return [comp.strip() for comp in self.competences.split(',') if comp.strip()]