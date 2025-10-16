from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # Interface RH principale
    path('rh/', views.interface_rh, name='interface_rh'),

    # Gestion des candidats (uniquement accessible par le RH)
    path('rh/candidats/<int:offre_id>/', views.liste_candidats, name='liste_candidats'),
    path('rh/candidat/<int:candidat_id>/', views.detail_candidat, name='detail_candidat'),
    path('rh/candidat/supprimer/<int:id>/', views.delete_candidat, name='delete_candidat'),
    path('candidat/ajouter/<int:offre_id>/', views.ajouter_candidat, name='ajouter_candidat'),

    # Pour l’instant, modifier/supprimer ne seront pas utilisés (réservés plus tard au candidat)
    path('candidat/delete/<int:candidat_id>/', views.delete_candidat, name='delete_candidat'),

    # ✅ Partie RH : gestion des offres d’emploi
    path('rh/offres/', views.liste_offres, name='liste_offres'),
    path('rh/offres/ajouter/', views.ajouter_offre, name='ajouter_offre'),
    path('rh/offres/<int:offre_id>/modifier/', views.modifier_offre, name='modifier_offre'),
    path('rh/offres/<int:offre_id>/supprimer/', views.supprimer_offre, name='supprimer_offre'),

    # ✅ Liste des candidats pour une offre spécifique
    path('rh/offres/<int:offre_id>/candidats/', views.candidats_pour_offre, name='candidats_pour_offre'),

    # ✅ Page d'inscription et de connexion
    path('', views.landing_page, name='landing'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='recrutement/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('redirect/', views.redirect_user, name='redirect_user'),

    # ✅ Page d'accueil
    path('home/', views.home, name='home'),
    path('interface_rh/', views.interface_rh, name='interface_rh'),
    path('postuler/<int:offre_id>/', views.postuler, name='postuler'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
