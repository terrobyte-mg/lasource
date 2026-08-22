from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'chambre', 'date_arrivee', 'date_depart', 'confirmee']
    list_filter = ['confirmee', 'date_arrivee']
    search_fields = ['nom', 'prenom', 'cin']