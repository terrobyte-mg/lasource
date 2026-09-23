#chambres\views.py
from django.shortcuts import render

from .models import Chambre, GalerieItem


def accueil(request):
    chambres = Chambre.objects.filter(disponible=True)
    galerie_items = GalerieItem.objects.filter(actif=True).prefetch_related('images')
    return render(request, 'chambres/accueil.html', {
        'chambres': chambres,
        'images_accueil': galerie_items,
    })

def chambres_accueil(request):
    chambres = Chambre.objects.all().order_by('disponible', '-created_at')
    return render(request, 'chambres/accueil.html', {'chambres': chambres})


def liste_chambres(request):
    chambres = Chambre.objects.filter(disponible=True)
    return render(request, 'chambres/liste.html', {'chambres': chambres})
