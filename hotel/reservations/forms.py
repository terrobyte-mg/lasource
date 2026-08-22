from django import forms
from django.core.exceptions import ValidationError
from .models import Reservation
from datetime import date, timedelta

# Configuration des indicatifs
INDICATIFS_VALIDES = {
    '+261': {'pays': 'Madagascar', 'longueur': 9},
    '+33':  {'pays': 'France', 'longueur': 9},
    '+254': {'pays': 'Kenya', 'longueur': 9},
    '+27':  {'pays': 'Afrique du Sud', 'longueur': 9},
    '+44':  {'pays': 'Royaume-Uni', 'longueur': 10},
    '+1':   {'pays': 'États-Unis/Canada', 'longueur': 10},
    '+49':  {'pays': 'Allemagne', 'longueur': 10},
    '+39':  {'pays': 'Italie', 'longueur': 9},
    '+34':  {'pays': 'Espagne', 'longueur': 9},
}

class ReservationForm(forms.ModelForm):
    # Champs de saisie temporaires (non dans le modèle)
    indicatif = forms.ChoiceField(
        choices=[('', 'Sélectionner')] + [(k, f"{k} ({v['pays']})") for k, v in INDICATIFS_VALIDES.items()],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_indicatif'}),
        label="Indicatif téléphonique"
    )
    telephone_saisie = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class' : 'form-control',
                                      'placeholder' : 'Ex: 341234567',
                                      'type' : 'tel',
                                      'inputmode' : 'number',
                                      'pattern' : '[0-9]*',
                                      'autocomplete' : 'tel',}),
        label="Numéro de téléphone"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Email"
    )

    class Meta:
        model = Reservation
        fields = ['nom', 'prenom', 'cin', 'adresse', 'emploi', 'email', 'chambre', 'date_arrivee', 'date_depart']
        widgets = {
            'date_arrivee': forms.DateInput(attrs={'class': 'form-control datepicker', 'placeholder': 'jj/mm/aaaa'}),
            'date_depart': forms.DateInput(attrs={'class': 'form-control datepicker', 'placeholder': 'jj/mm/aaaa'}),
            'chambre': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            elif 'form-control' not in field.widget.attrs['class']:
                field.widget.attrs['class'] += ' form-control'

        # Pré-remplir si instance existe
        if self.instance and self.instance.pk and self.instance.telephone:
            tel = self.instance.telephone
            if tel.startswith('+'):
                for indic in INDICATIFS_VALIDES:
                    if tel.startswith(indic):
                        self.fields['indicatif'].initial = indic
                        self.fields['telephone_saisie'].initial = tel[len(indic):]
                        break

    def clean_telephone_saisie(self):
        indicatif = self.cleaned_data.get('indicatif')
        numero = self.cleaned_data.get('telephone_saisie')

        if not indicatif or not numero:
            raise ValidationError("Veuillez fournir un indicatif et un numéro.")

        # Supprimer les espaces, tirets, etc.
        numero = ''.join(filter(str.isdigit, numero))

        if indicatif not in INDICATIFS_VALIDES:
            raise ValidationError("Indicatif non pris en charge.")

        longueur_attendue = INDICATIFS_VALIDES[indicatif]['longueur']
        if len(numero) != longueur_attendue:
            pays = INDICATIFS_VALIDES[indicatif]['pays']
            raise ValidationError(f"Le numéro pour {pays} doit contenir exactement {longueur_attendue} chiffres.")

        # Combiner en format E.164
        telephone_complet = indicatif + numero
        return telephone_complet

    def clean(self):
        cleaned = super().clean()
        arr = cleaned.get('date_arrivee')
        dep = cleaned.get('date_depart')
        chambre = cleaned.get('chambre')

        # Validation des dates
        if arr and dep:
            tomorrow = date.today() + timedelta(days=1)
            if arr < tomorrow:
                raise ValidationError("La date d’arrivée doit être au moins demain.")
            if dep <= arr:
                raise ValidationError("La date de départ doit être postérieure à la date d’arrivée.")

            # Vérification de disponibilité
            from .models import Reservation as ResaModel
            qs = ResaModel.objects.filter(
                chambre=chambre,
                date_depart__gt=arr,
                date_arrivee__lt=dep
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Cette chambre est déjà réservée sur ce créneau.")

        # Ajouter le téléphone combiné au cleaned_data final
        if 'telephone_saisie' in cleaned:
            cleaned['telephone'] = cleaned['telephone_saisie']

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.telephone = self.cleaned_data['telephone']
        if commit:
            instance.save()
        return instance