# recrutement/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Candidat
from .forms import CandidatForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator

def liste_candidats(request):
    candidats = Candidat.objects.all()
    paginator = Paginator(candidats, 10)  # 10 candidats par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'recrutement/liste_candidats.html', {'page_obj': page_obj})

def detail_candidat(request, candidat_id):
    candidat = get_object_or_404(Candidat, pk=candidat_id)  # Récupère un candidat par son ID
    return render(request, 'recrutement/detail_candidat.html', {'candidat': candidat})

def ajouter_candidat(request):
    if request.method == "POST":
        form = CandidatForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Enregistre le candidat
            print("Formulaire valide, redirection vers /candidats/")
            return redirect('/candidats/')  # Redirige vers /candidats/
        else:
            print("Formulaire invalide", form.errors)  # Affiche les erreurs du formulaire
    else:
        form = CandidatForm()
    
    return render(request, 'recrutement/ajouter_candidat.html', {'form': form})

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