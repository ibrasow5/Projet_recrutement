from django import forms
from .models import Candidat, OffreEmploi, Utilisateur
from django.contrib.auth.forms import UserCreationForm

class CandidatForm(forms.ModelForm):
    class Meta:
        model = Candidat
        fields = ['cv']
        
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
        fields = [
            'entreprise', 'logo', 'localisation', 'titre', 'description',
            'type_contrat', 'salaire_min', 'salaire_max', 'competences',
            'temps_plein', 'urgent', 'date_limite'
        ]
        widgets = {
            'date_limite': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'competences': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Ex: JavaScript, ServiceNow, ITIL, API REST'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})

class CustomUserCreationForm(UserCreationForm):
    prenom = forms.CharField(
        max_length=100,
        required=True,
        label='Prénom',
        widget=forms.TextInput(attrs={
            'placeholder': 'Votre prénom',
            'class': 'form-control'
        })
    )
    nom = forms.CharField(
        max_length=100,
        required=True,
        label='Nom',
        widget=forms.TextInput(attrs={
            'placeholder': 'Votre nom',
            'class': 'form-control'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'votre.email@exemple.com',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Utilisateur
        fields = ('prenom', 'nom', 'username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.prenom = self.cleaned_data['prenom']
        user.nom = self.cleaned_data['nom']
        user.role = 'candidat'  # Force le rôle à candidat
        if commit:
            user.save()
        return user

class CvUploadForm(forms.Form):
    cv = forms.FileField(
        label='Télécharger votre CV',
        help_text='Formats acceptés : PDF, DOC, DOCX. Taille max : 2MB.',
    )

    def clean_cv(self):
        cv = self.cleaned_data.get('cv')
        if cv:
            if cv.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Le fichier est trop volumineux (max 2MB).")
            if not cv.name.lower().endswith(('.pdf', '.doc', '.docx')):
                raise forms.ValidationError("Format non supporté.")
        return cv