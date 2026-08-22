from django.db import models

from chambres.models import Chambre


class Reservation(models.Model):
    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    cin = models.CharField(max_length=20)
    adresse = models.CharField(max_length=100)
    emploi = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    date_arrivee = models.DateField()
    date_depart = models.DateField()
    confirmee = models.BooleanField(default=False)
    payee = models.BooleanField(default=False)
    date_payee = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} {self.prenom} – {self.chambre.numero}"