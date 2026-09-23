from django.test import TestCase
from django.urls import reverse

from .models import Chambre


class ChambresViewsTests(TestCase):
    def test_liste_ne_retourne_que_les_chambres_disponibles(self):
        disponible = Chambre.objects.create(
            numero='101',
            type='Simple',
            prix=100000,
            description='Desc',
            caracteristiques='WiFi',
            disponible=True,
        )
        Chambre.objects.create(
            numero='102',
            type='Double',
            prix=120000,
            description='Desc',
            caracteristiques='WiFi',
            disponible=False,
        )

        response = self.client.get(reverse('chambres:liste'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(disponible, response.context['chambres'])
        self.assertEqual(response.context['chambres'].count(), 1)
