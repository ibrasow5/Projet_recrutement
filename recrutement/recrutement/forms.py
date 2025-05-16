from django import forms
from .models import Candidat, OffreEmploi, Utilisateur
from django.contrib.auth.forms import UserCreationForm

class CandidatForm(forms.ModelForm):
    class Meta:
        model = Candidat
        fields = ['prenom', 'nom', 'email', 'cv', 'date_naissance', 'telephone']  # Inclure tous les champs nécessaires
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),  # Pour afficher un calendrier pour la date
        }

    def __init__(self, *args, **kwargs):
        super(CandidatForm, self).__init__(*args, **kwargs)
        # Ajouter des classes Bootstrap à tous les champs
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Candidat.objects.filter(email=email).exists():
            raise forms.ValidationError("Un candidat avec cet email existe déjà.")
        return email
    
class OffreForm(forms.ModelForm):
    class Meta:
        model = OffreEmploi
        fields = ['titre', 'description', 'date_limite']
        widgets = {
            'date_limite': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = ('username', 'email', 'role', 'password1', 'password2')
