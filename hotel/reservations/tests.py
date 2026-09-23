from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from chambres.models import Chambre
from .models import Reservation


class ReservationViewsTests(TestCase):
    def setUp(self):
        self.chambre = Chambre.objects.create(
            numero='201',
            type='Simple',
            prix=100000,
            description='Desc',
            caracteristiques='WiFi',
            disponible=True,
        )

    def test_formulaire_preremplit_chambre_depuis_querystring(self):
        response = self.client.get(reverse('reservations:reserver'), {'chambre': self.chambre.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            str(response.context['form'].initial.get('chambre')),
            str(self.chambre.id),
        )

    def test_refuse_double_reservation_sur_periode(self):
        tomorrow = timezone.localdate() + timedelta(days=1)
        Reservation.objects.create(
            chambre=self.chambre,
            nom='Client',
            prenom='A',
            cin='CIN1',
            adresse='Adr',
            emploi='Job',
            telephone='+261341234567',
            email='a@example.com',
            date_arrivee=tomorrow + timedelta(days=2),
            date_depart=tomorrow + timedelta(days=5),
        )

        response = self.client.post(
            reverse('reservations:reserver'),
            data={
                'nom': 'Client2',
                'prenom': 'B',
                'cin': 'CIN2',
                'adresse': 'Adr',
                'emploi': 'Job',
                'email': 'b@example.com',
                'chambre': self.chambre.id,
                'indicatif': '+261',
                'telephone_saisie': '341234568',
                'date_arrivee': (tomorrow + timedelta(days=3)).strftime('%d/%m/%Y'),
                'date_depart': (tomorrow + timedelta(days=6)).strftime('%d/%m/%Y'),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "déjà réservée")
