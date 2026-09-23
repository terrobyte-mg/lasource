from datetime import datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET

from chambres.models import Chambre
from .forms import ReservationForm
from .models import Reservation  # Assure-toi que c’est importé


def reserver(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            # Optionnel : associer un utilisateur si connecté
            # if request.user.is_authenticated:
            #     reservation.client = request.user
            reservation.save()
            return redirect('reservations:confirmation')
    else:
        initial = {}
        chambre_id = request.GET.get('chambre')
        if chambre_id and Chambre.objects.filter(id=chambre_id, disponible=True).exists():
            initial['chambre'] = chambre_id
        form = ReservationForm(initial=initial)
    return render(request, 'reservations/reserver.html', {'form': form})


@require_GET
def dates_bloquees_api(request):
    ch_id = request.GET.get('chambre')
    if not ch_id:
        return JsonResponse({'dates': []})

    reservations = Reservation.objects.filter(
        chambre_id=ch_id,
        confirmee=True
    )

    blocked = [
        (r.date_arrivee + timedelta(days=i)).strftime('%d/%m/%Y')
        for r in reservations
        for i in range((r.date_depart - r.date_arrivee).days)
    ]

    return JsonResponse({'dates': blocked})


@require_GET
def disponibilite_api(request):
    """Renvoie les chambres libres sur le créneau donné."""
    try:
        arr = datetime.strptime(request.GET.get('arrivee'), '%d/%m/%Y').date()
        dep = datetime.strptime(request.GET.get('depart'), '%d/%m/%Y').date()
        if dep <= arr:
            return JsonResponse({'chambres': []})
    except (ValueError, TypeError):
        return JsonResponse({'chambres': []})

    chambres = Chambre.objects.exclude(
        reservation__date_depart__gt=arr,
        reservation__date_arrivee__lt=dep
    ).filter(disponible=True)

    data = [
        {'id': c.id, 'numero': c.numero, 'type': c.get_type_display()}
        for c in chambres
    ]
    return JsonResponse({'chambres': data})


def liste_chambres(request):
    chambres = Chambre.objects.filter(disponible=True)
    return render(request, 'chambres/liste.html', {'chambres': chambres})


def confirmation(request):
    return render(request, 'reservations/confirmation.html')
