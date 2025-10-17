# recrutement/views.py
import io
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404, redirect
from .models import OffreEmploi, Candidat, RH, Rapport
from .forms import CandidatForm, OffreForm, CustomUserCreationForm, CvUploadForm
from django.contrib.auth import login, logout, get_user_model
from django.http import HttpResponseRedirect, FileResponse, HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfgen import canvas

def liste_candidats(request, offre_id):
    offre = get_object_or_404(OffreEmploi, id=offre_id, recruteur=request.user)
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
    # Offres du RH connecté uniquement
    offres = OffreEmploi.objects.filter(recruteur=request.user)

    # Candidats uniquement pour les offres de ce RH
    candidats = Candidat.objects.select_related('user', 'offre').filter(offre__recruteur=request.user)

    matchings = []
    # Dictionnaire pour stocker les scores par offre
    scores_par_offre = {}
    tous_les_scores = []  # Pour le score moyen global
    
    for candidat in candidats:
        if candidat.user and candidat.offre:
            score = min(100, (len(candidat.user.get_full_name()) * 4) + (len(candidat.offre.titre) % 20) * 3)
            matchings.append({
                'candidat': candidat,
                'offre': candidat.offre,
                'score': score
            })
            
            # Ajouter le score au dictionnaire par offre
            offre_id = candidat.offre.id
            if offre_id not in scores_par_offre:
                scores_par_offre[offre_id] = []
            scores_par_offre[offre_id].append(score)
            
            # Ajouter à la liste globale
            tous_les_scores.append(score)
    
    # 🔽 Tri du plus haut score au plus bas
    matchings = sorted(matchings, key=lambda x: x['score'], reverse=True)
    
    # Calculer la moyenne des scores pour chaque offre
    for offre in offres:
        if offre.id in scores_par_offre:
            scores = scores_par_offre[offre.id]
            offre.score_moyen = round(sum(scores) / len(scores))
        else:
            offre.score_moyen = 0
    
    # Calculer le score moyen global
    score_moyen_global = round(sum(tous_les_scores) / len(tous_les_scores)) if tous_les_scores else 0

    context = {
        'offres': offres,
        'candidats': candidats,
        'matchings': matchings,
        'score_moyen_global': score_moyen_global,  # ← Nouveau
    }

    return render(request, 'recrutement/interface_rh.html', context)


def ajouter_offre(request):
    if request.method == "POST":
        form = OffreForm(request.POST, request.FILES)  # ← IMPORTANT : request.FILES
        if form.is_valid():
            offre = form.save(commit=False)
            offre.recruteur = request.user
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

# Vue pour modifier une offre
@login_required
def modifier_offre(request, offre_id):
    # Récupérer l'offre (assurez-vous que le recruteur est le propriétaire)
    offre = get_object_or_404(OffreEmploi, id=offre_id)
    
    if request.method == 'POST':
        try:
            # Mise à jour des champs
            offre.titre = request.POST.get('titre')
            offre.entreprise = request.POST.get('entreprise')
            offre.localisation = request.POST.get('localisation')
            offre.type_contrat = request.POST.get('type_contrat')
            offre.description = request.POST.get('description')
            offre.competences = request.POST.get('competences')
            offre.date_limite = request.POST.get('date_limite')
            
            # Salaires (optionnels)
            salaire_min = request.POST.get('salaire_min')
            salaire_max = request.POST.get('salaire_max')
            offre.salaire_min = int(salaire_min) if salaire_min else None
            offre.salaire_max = int(salaire_max) if salaire_max else None
            
            # Checkboxes (BooleanField)
            offre.temps_plein = 'temps_plein' in request.POST
            offre.urgent = 'urgent' in request.POST
            offre.nouveau = 'nouveau' in request.POST
            
            # Gestion du logo (si un nouveau fichier est uploadé)
            if 'logo' in request.FILES:
                offre.logo = request.FILES['logo']
            
            offre.save()
            
            messages.success(request, f"L'offre '{offre.titre}' a été modifiée avec succès !")
            return redirect('interface_rh')
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification : {str(e)}")
    
    return render(request, 'recrutement/modifier_offre.html', {'offre': offre})


@login_required
def supprimer_offre(request, offre_id):
    print(f"========== SUPPRESSION APPELÉE ==========")
    print(f"Method: {request.method}")
    print(f"Offre ID: {offre_id}")
    
    if request.method == 'POST':
        try:
            offre = get_object_or_404(OffreEmploi, id=offre_id)
            print(f"Offre trouvée: {offre.titre}")
            titre = offre.titre
            offre.delete()
            print(f"Offre supprimée: {titre}")
            messages.success(request, f"L'offre '{titre}' a été supprimée avec succès.")
        except Exception as e:
            print(f"ERREUR: {e}")
            messages.error(request, f"Erreur: {str(e)}")
    else:
        print("Pas de POST, redirection...")
    
    return redirect('interface_rh')

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
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'recruteur':
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
    # Récupérer le premier candidat ou en créer un
    try:
        candidat = Candidat.objects.filter(user=request.user).first()
        if not candidat:
            candidat = Candidat.objects.create(user=request.user, score_matching=0)
    except Exception as e:
        # En cas d'erreur, créer un nouveau
        candidat = Candidat.objects.create(user=request.user, score_matching=0)
    
    # Upload CV si POST
    if request.method == 'POST' and request.FILES.get('cv'):
        candidat.cv = request.FILES['cv']
        candidat.save()
        messages.success(request, 'Votre CV a été mis à jour avec succès !')
        return redirect('profil')
    
    # Statistiques - Nombre d'offres auxquelles le candidat a postulé
    nb_candidatures = Candidat.objects.filter(user=request.user, offre__isnull=False).count()
    nb_offres_actives = OffreEmploi.objects.count()
    
    context = {
        'candidat': candidat,
        'nb_candidatures': nb_candidatures,
        'nb_offres_actives': nb_offres_actives,
    }
    
    return render(request, 'recrutement/profil.html', context)


User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Supprimer un utilisateur
        if action == 'delete':
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                user.delete()
                messages.success(request, f'Utilisateur {user.get_full_name()} supprimé avec succès.')
            except User.DoesNotExist:
                messages.error(request, 'Utilisateur introuvable.')
            return redirect('admin_dashboard')
        
        # Ajouter un recruteur
        elif action == 'add':
            prenom = request.POST.get('prenom')
            nom = request.POST.get('nom')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            entreprise = request.POST.get('entreprise')
            
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    prenom=prenom,
                    nom=nom,
                    role='recruteur'
                )
                # Créer le profil RH
                from .models import RH
                RH.objects.create(user=user, entreprise=entreprise)
                
                messages.success(request, f'Recruteur {user.get_full_name()} créé avec succès.')
            except Exception as e:
                messages.error(request, f'Erreur lors de la création : {str(e)}')
            return redirect('admin_dashboard')
    
    # Récupérer les utilisateurs
    candidats = User.objects.filter(role='candidat').order_by('-date_joined')
    recruteurs = User.objects.filter(role='recruteur').order_by('-date_joined')
    
    # Statistiques
    nb_candidats = candidats.count()
    nb_recruteurs = recruteurs.count()
    nb_offres = OffreEmploi.objects.count()
    
    context = {
        'candidats': candidats,
        'recruteurs': recruteurs,
        'nb_candidats': nb_candidats,
        'nb_recruteurs': nb_recruteurs,
        'nb_offres': nb_offres,
    }
    
    return render(request, 'recrutement/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.prenom = request.POST.get('prenom')
        user.nom = request.POST.get('nom')
        user.email = request.POST.get('email')
        user.username = request.POST.get('username')
        
        # Si c'est un recruteur, mettre à jour l'entreprise
        if user.role == 'recruteur':
            entreprise = request.POST.get('entreprise')
            rh, created = RH.objects.get_or_create(user=user)
            rh.entreprise = entreprise
            rh.save()
        
        # Changer le mot de passe si fourni
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        user.save()
        messages.success(request, f'Utilisateur {user.get_full_name()} modifié avec succès.')
        return redirect('admin_dashboard')
    
    # Si c'est un recruteur, récupérer l'entreprise
    entreprise = ''
    if user.role == 'recruteur':
        try:
            rh = RH.objects.get(user=user)
            entreprise = rh.entreprise
        except RH.DoesNotExist:
            entreprise = ''
    
    context = {
        'user': user,
        'entreprise': entreprise,
    }
    
    return render(request, 'recrutement/edit_user.html', context)


@login_required
def generer_rapport_simple(request):
    # 🔹 Récupérer les paramètres
    type_rapport = request.POST.get('report_type', 'offres')  # "offres" ou "candidatures"
    periode = request.POST.get('report_period', 'month')
    user = request.user  # Recruteur connecté

    # 🔹 Nom du fichier
    filename = f"rapport_{type_rapport}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    # 🔹 Création d’un buffer mémoire pour le PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    largeur, hauteur = A4
    y = hauteur - 2*cm

    # 🔹 Métadonnées du PDF
    titre_document = f"RAPPORT DES {type_rapport.upper()} - {periode.upper()}"
    p.setTitle(titre_document)
    p.setAuthor("TalentMatch RH")
    p.setSubject(f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    p.setCreator("TalentMatch RH")

    # 🔹 En-tête
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(largeur / 2, y, titre_document)
    y -= 1.2*cm
    p.setFont("Helvetica", 10)
    p.drawString(2*cm, y, f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    y -= 0.8*cm

    # 🔹 Corps du rapport selon le type
    if type_rapport == "offres":
        offres = OffreEmploi.objects.filter(recruteur=user).order_by('-date_publication')[:50]
        p.drawString(2*cm, y, f"Total d'offres : {offres.count()}")
        y -= 1*cm
        p.line(2*cm, y, largeur - 2*cm, y)
        y -= 0.5*cm

        for i, offre in enumerate(offres, 1):
            if y < 3*cm:
                p.showPage()
                y = hauteur - 2*cm

            p.setFont("Helvetica-Bold", 12)
            p.drawString(2*cm, y, f"{i}. {offre.titre}")
            y -= 0.5*cm

            p.setFont("Helvetica", 10)
            p.drawString(2.5*cm, y, f"Entreprise: {offre.entreprise}")
            y -= 0.4*cm
            p.drawString(2.5*cm, y, f"Localisation: {offre.localisation}")
            y -= 0.4*cm
            p.drawString(2.5*cm, y, f"Type de contrat: {offre.type_contrat}")
            y -= 0.4*cm
            p.drawString(2.5*cm, y, f"Salaire: {offre.get_salaire_display()}")
            y -= 0.4*cm
            p.drawString(2.5*cm, y, f"Compétences: {', '.join(offre.get_competences_list())}")
            y -= 0.4*cm
            p.drawString(2.5*cm, y, f"Date limite: {offre.date_limite.strftime('%d/%m/%Y')}")
            y -= 0.6*cm
            p.line(2*cm, y, largeur - 2*cm, y)
            y -= 0.8*cm

    elif type_rapport == "candidatures":
        candidatures = Candidat.objects.filter(offre__recruteur=user).select_related('user', 'offre')[:50]
        p.drawString(2*cm, y, f"Total de candidatures : {candidatures.count()}")
        y -= 1*cm
        p.line(2*cm, y, largeur - 2*cm, y)
        y -= 0.5*cm

        for i, cand in enumerate(candidatures, 1):
            if y < 3*cm:
                p.showPage()
                y = hauteur - 2*cm

            full_name = cand.user.get_full_name() if cand.user else "Candidat anonyme"
            p.setFont("Helvetica-Bold", 12)
            p.drawString(2*cm, y, f"{i}. {full_name}")
            y -= 0.5*cm

            p.setFont("Helvetica", 10)
            if cand.offre:
                p.drawString(2.5*cm, y, f"Offre: {cand.offre.titre} ({cand.offre.entreprise})")
                y -= 0.4*cm
            if cand.user and cand.user.email:
                p.drawString(2.5*cm, y, f"Email: {cand.user.email}")
                y -= 0.4*cm
            p.drawString(2.5*cm, y, f"CV: {'Oui' if cand.cv else 'Non'}")
            y -= 0.4*cm
            p.line(2*cm, y, largeur - 2*cm, y)
            y -= 0.8*cm

    else:
        p.drawString(2*cm, y, "⚠️ Type de rapport inconnu. Utilisez 'offres' ou 'candidatures'.")

    # 🔹 Pied de page
    p.setFont("Helvetica-Oblique", 9)
    p.drawCentredString(largeur / 2, 1.5*cm, "Fin du rapport - TalentMatch RH")

    p.showPage()
    p.save()

    # 🔹 Récupérer le contenu PDF
    buffer.seek(0)
    pdf_data = buffer.getvalue()

    # 🔹 Sauvegarder le rapport dans la base
    rapport = Rapport(
        recruteur=user,
        type_rapport=type_rapport,
        periode=periode,
        titre=titre_document,
    )
    rapport.fichier.save(filename, ContentFile(pdf_data))
    rapport.save()

    # 🔹 Envoyer le PDF en réponse pour téléchargement immédiat
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def telecharger_rapport(request, rapport_id):
    rapport = get_object_or_404(Rapport, id=rapport_id, recruteur=request.user)
    
    response = FileResponse(rapport.fichier.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{rapport.titre}.pdf"'
    
    return response