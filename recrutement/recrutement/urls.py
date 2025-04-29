from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('candidats/', views.liste_candidats, name='liste_candidats'),
    path('candidat/<int:candidat_id>/', views.detail_candidat, name='detail_candidat'),
    path('candidat/ajouter/', views.ajouter_candidat, name='ajouter_candidat'),
    path('candidat/modifier/<int:id>/', views.update_candidat, name='update_candidat'),
    path('candidat/supprimer/<int:id>/', views.delete_candidat, name='delete_candidat'),
]
