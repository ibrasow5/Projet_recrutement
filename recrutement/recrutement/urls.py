from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Interface RH principale
    path('rh/', views.interface_rh, name='interface_rh'),

    # Gestion des candidats (uniquement accessible par le RH)
    path('rh/candidats/', views.liste_candidats, name='liste_candidats'),
    path('rh/candidat/<int:candidat_id>/', views.detail_candidat, name='detail_candidat'),
    path('rh/candidat/supprimer/<int:id>/', views.delete_candidat, name='delete_candidat'),
    path('candidat/ajouter/', views.ajouter_candidat, name='ajouter_candidat'),

    # Pour l’instant, modifier/supprimer ne seront pas utilisés (réservés plus tard au candidat)
    # Mais tu peux les conserver si besoin
    path('candidat/modifier/<int:id>/', views.update_candidat, name='update_candidat'),
    path('candidat/supprimer/<int:id>/', views.delete_candidat, name='delete_candidat'),

    # ✅ Partie RH : gestion des offres d’emploi
    path('rh/offres/', views.liste_offres, name='liste_offres'),
    path('rh/offres/ajouter/', views.ajouter_offre, name='ajouter_offre'),
    path('rh/offres/<int:offre_id>/modifier/', views.modifier_offre, name='modifier_offre'),
    path('rh/offres/<int:offre_id>/supprimer/', views.supprimer_offre, name='supprimer_offre'),

    # ✅ Liste des candidats pour une offre spécifique
    path('rh/offres/<int:offre_id>/candidats/', views.candidats_pour_offre, name='candidats_pour_offre'),

    # À utiliser plus tard pour inscription publique ou côté candidat
    path('candidat/ajouter/', views.ajouter_candidat, name='ajouter_candidat'),
    path('candidat/modifier/<int:id>/', views.update_candidat, name='update_candidat'),
]
