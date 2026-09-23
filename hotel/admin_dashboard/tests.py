from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from chambres.models import ImageAccueil


class AdminDashboardSecurityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='secret1234',
        )
        self.image = ImageAccueil.objects.create(
            image=SimpleUploadedFile(
                'test.jpg',
                b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',
                content_type='image/gif',
            ),
            description='Image test',
            actif=True,
        )

    def test_ajout_image_accueil_requiert_authentification(self):
        response = self.client.post(
            reverse('admin_dashboard:images_accueil_ajouter'),
            data={'description': 'Nouvelle'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin_dashboard:login'), response.url)

    def test_toggle_image_accepte_uniquement_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('admin_dashboard:images_accueil_toggle', args=[self.image.id]))
        self.assertEqual(response.status_code, 405)
