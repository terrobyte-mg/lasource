# chambres/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Chambre(models.Model):
    TYPE_CHOICES = [
        ('Simple', 'Simple'),
        ('Double', 'Double'),
        ('Familiale', 'Familiale'),
    ]

    numero = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Numéro",
        help_text="Identifiant unique de la chambre"
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Type de chambre"
    )
    prix = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Prix par nuit",
        help_text="Prix en Ariary"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Description détaillée de la chambre"
    )
    caracteristiques = models.TextField(
        verbose_name="Caractéristiques",
        help_text="Équipements et services disponibles"
    )
    disponible = models.BooleanField(
        default=True,
        verbose_name="Disponible",
        help_text="Cochez pour rendre visible sur le site"
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifiée le")

    class Meta:
        verbose_name = "Chambre"
        verbose_name_plural = "Chambres"
        ordering = ['numero']

    def __str__(self):
        return f"Chambre {self.numero} ({self.type})"

    def clean(self):
        """Validation personnalisée"""
        if self.prix and self.prix < 0:
            raise ValidationError({'prix': 'Le prix ne peut pas être négatif.'})

    @property
    def image_principale(self):
        """Retourne la première image ou None"""
        return self.images.first()

    @property
    def nombre_images(self):
        """Compte le nombre d'images"""
        return self.images.count()


class ChambreImage(models.Model):
    chambre = models.ForeignKey(
        Chambre,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Chambre"
    )
    image = models.ImageField(
        upload_to='chambres/gallery/',
        verbose_name="Image",
        help_text="Formats acceptés: JPG, PNG, WEBP"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploadée le")

    class Meta:
        verbose_name = "Image de chambre"
        verbose_name_plural = "Images de chambres"
        ordering = ['uploaded_at']

    def __str__(self):
        return f"Photo de la chambre {self.chambre.numero}"

class ImageAccueil(models.Model):
    image = models.ImageField(upload_to='accueil/')
    description = models.CharField(max_length=255)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description

class GalerieItem(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    ordre = models.IntegerField(default=0, help_text="ordre d'affichage")
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item de Galerie"
        verbose_name_plural = "Items de Galerie"
        ordering = ['ordre', '-created_at']

    def __str__(self):
        return self.titre

class GalerieImage(models.Model):
    item = models.ForeignKey(
        GalerieItem,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Item de Galerie"
    )
    image = models.ImageField(
        upload_to='galerie/',
        verbose_name="Image",
    )
    description = models.CharField(max_length=255, blank=True)
    ordre = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Image de galerie"
        verbose_name_plural = "Images de galerie"
        ordering = ['ordre', '-uploaded_at']

    def __str__(self):
        return f"Image de {self.item.titre}"