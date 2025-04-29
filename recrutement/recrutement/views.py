# recrutement/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import OffreEmploi, Candidat
from .forms import CandidatForm, OffreForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages

def liste_candidats(request, offre_id):
    offre = get_object_or_404(OffreEmploi, id=offre_id)
    candidats = Candidat.objects.filter(offre=offre)  # Récupère tous les candidats pour l'offre spécifique
    # Pagination
    paginator = Paginator(candidats, 10)  # 10 candidats par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'recrutement/liste_candidats.html', {'candidats': candidats, 'offre': offre})

def detail_candidat(request, candidat_id):
    candidat = get_object_or_404(Candidat, pk=candidat_id)  # Récupère un candidat par son ID
    return render(request, 'recrutement/detail_candidat.html', {'candidat': candidat})

def ajouter_candidat(request, offre_id):
    offre = OffreEmploi.objects.get(id=offre_id)
    
    if request.method == 'POST':
        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            candidat = form.save(commit=False)
            candidat.offre = offre
            candidat.save()
            return redirect('liste_candidats', offre_id=offre.id)  # 👈 doit correspondre à l’URL déclarée
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

def delete_candidat(request, id):
    candidat = Candidat.objects.get(id=id)
    candidat.delete()
    return HttpResponseRedirect(reverse('recrutement/liste_candidats'))

def interface_rh(request):
    offres = OffreEmploi.objects.all()
    return render(request, 'recrutement/interface_rh.html', {'offres': offres})

def ajouter_offre(request):
    form = OffreForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('interface_rh')
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