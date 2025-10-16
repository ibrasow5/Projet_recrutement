# recrutement/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import OffreEmploi, Candidat
from .forms import CandidatForm, OffreForm, CustomUserCreationForm, CvUploadForm
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def liste_candidats(request, offre_id):
    offre = get_object_or_404(OffreEmploi, id=offre_id)
    candidats = offre.candidats.all()  # grâce au related_name

    # Pagination
    paginator = Paginator(candidats, 10)  # 10 candidats par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'recrutement/liste_candidats.html', {
        'offre': offre,
        'candidats': candidats
    })
    

def detail_candidat(request, candidat_id):
    candidat = get_object_or_404(Candidat, pk=candidat_id)  # Récupère un candidat par son ID
    return render(request, 'recrutement/detail_candidat.html', {'candidat': candidat})

def ajouter_candidat(request, offre_id):
    offre = get_object_or_404(OffreEmploi, pk=offre_id)
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            candidat = form.save(commit=False)
            candidat.offre = offre
            candidat.save()
            return redirect('liste_candidats', offre_id=offre.id)
    else:
        form = CandidatForm()
    return render(request, 'recrutement/ajouter_candidat.html', {'form': form, 'offre': offre})

def update_candidat(request, id):
    candidat = Candidat.objects.get(id=id)
    if request.method == 'POST':
        form = CandidatForm(request.POST, instance=candidat)
        if form.is_valid():
            form.save()
            return redirect('recrutement/details_candidat', id=candidat.id)
    else:
        form = CandidatForm(instance=candidat)
    return render(request, 'recrutement/update.html', {'form': form})

def delete_candidat_old(request, id):
    candidat = Candidat.objects.get(id=id)
    candidat.delete()
    return HttpResponseRedirect(reverse('recrutement/liste_candidats'))

def interface_rh(request):
    offres = OffreEmploi.objects.all()
    candidats = Candidat.objects.select_related('user', 'offre').all()

    matchings = []
    for candidat in candidats:
        if candidat.user and candidat.offre:
            score = min(100, (len(candidat.user.get_full_name()) * 4) + (len(candidat.offre.titre) % 20) * 3)
            matchings.append({
                'candidat': candidat,
                'offre': candidat.offre,
                'score': score
            })

    # 🔽 Tri du plus haut score au plus bas
    matchings = sorted(matchings, key=lambda x: x['score'], reverse=True)

    context = {
        'offres': offres,
        'candidats': candidats,
        'matchings': matchings,
    }

    return render(request, 'recrutement/interface_rh.html', context)


def ajouter_offre(request):
    if request.method == "POST":
        form = OffreForm(request.POST, request.FILES)  # ← IMPORTANT : request.FILES
        if form.is_valid():
            offre = form.save(commit=False)
            offre.nb_candidats = 0  # Initialiser à 0
            offre.save()
            messages.success(request, "Offre publiée avec succès!")
            return redirect('interface_rh')
        else:
            messages.error(request, "Erreur lors de la création de l'offre. Vérifiez les champs.")
    else:
        form = OffreForm()
    return render(request, 'recrutement/ajouter_offre.html', {'form': form})

def candidats_pour_offre(request, offre_id):
    offre = get_object_or_404(OffreEmploi, pk=offre_id)
    candidats = offre.candidats.all()
    return render(request, 'recrutement/liste_candidats.html', {
        'offre': offre,
        'candidats': candidats,
    })

def liste_offres(request):
    offres = OffreEmploi.objects.all().order_by('-date_publication')
    return render(request, 'offres/liste_offres.html', {'offres': offres})

def modifier_offre(request, offre_id):
    offre = get_object_or_404(OffreEmploi, id=offre_id)
    if request.method == 'POST':
        form = OffreForm(request.POST, instance=offre)
        if form.is_valid():
            form.save()
            messages.success(request, 'Offre modifiée avec succès.')
            return redirect('liste_offres')
    else:
        form = OffreForm(instance=offre)
    return render(request, 'offres/modifier_offre.html', {'form': form, 'offre': offre})

def supprimer_offre(request, offre_id):
    offre = get_object_or_404(OffreEmploi, id=offre_id)
    if request.method == 'POST':
        offre.delete()
        messages.success(request, 'Offre supprimée avec succès.')
        return redirect('liste_offres')
    return render(request, 'offres/confirmer_suppression.html', {'offre': offre})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Bienvenue {user.get_full_name()} ! Votre compte a été créé avec succès.")
            login(request, user)
            return redirect('/redirect/')
        else:
            messages.error(request, "Erreur lors de la création du compte. Veuillez vérifier les informations.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'recrutement/register.html', {'form': form})

@login_required
def redirect_user(request):
    print(f"user connecté: {request.user.get_full_name()}, role: {request.user.role}")
    if request.user.role == 'recruteur':
        return redirect('interface_rh')
    else:
        return redirect('home')

def home(request):
    offres = OffreEmploi.objects.order_by('-date_publication')  # tri par date décroissante
    return render(request, 'recrutement/home.html', {'offres': offres})

@login_required
def postuler(request, offre_id):
    print("📩 POSTULER: Début de la vue")

    offre = get_object_or_404(OffreEmploi, id=offre_id)
    print(f"📝 Offre trouvée : {offre.titre} (id: {offre.id})")

    if request.method == 'POST':
        print("🛂 Méthode POST détectée")
        print(f"📦 FILES : {request.FILES}")
        print(f"🧾 POST : {request.POST}")

        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            print("✅ Formulaire valide")
            candidat = form.save(commit=False)
            candidat.user = request.user
            candidat.offre = offre
            candidat.save()
            print(f"💾 Candidat enregistré : {candidat}")
            messages.success(request, f'Votre candidature pour "{offre.titre}" a été envoyée avec succès !')
            return redirect('home')
        else:
            print("❌ Formulaire invalide")
            print(form.errors)
            messages.error(request, 'Erreur lors de l\'envoi du CV. Veuillez réessayer.')
            return redirect('home')
    else:
        print("📭 Méthode GET détectée")
        form = CandidatForm()

    return redirect('home')

def delete_candidat(request, candidat_id):
    candidat = get_object_or_404(Candidat, id=candidat_id)
    candidat.delete()
    messages.success(request, "Candidat supprimé avec succès.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def landing_page(request):
    # Si l'utilisateur est déjà connecté, rediriger selon son rôle
    if request.user.is_authenticated:
        if request.user.role == 'recruteur':
            return redirect('interface_rh')
        else:
            return redirect('home')
    return render(request, 'recrutement/landing.html')

def logout_view(request):
    logout(request)
    return redirect('landing')  # Redirection vers la landing page

@login_required
def profil(request):
    # Récupérer ou créer le profil candidat
    candidat, created = Candidat.objects.get_or_create(user=request.user)
    
    # Upload CV si POST
    if request.method == 'POST' and request.FILES.get('cv'):
        candidat.cv = request.FILES['cv']
        candidat.save()
        messages.success(request, 'Votre CV a été mis à jour avec succès !')
        return redirect('profil')
    
    # Statistiques
    nb_candidatures = Candidat.objects.filter(user=request.user).count()
    nb_offres_actives = OffreEmploi.objects.count()
    
    context = {
        'candidat': candidat,
        'nb_candidatures': nb_candidatures,
        'nb_offres_actives': nb_offres_actives,
    }
    
    return render(request, 'recrutement/profil.html', context)