# admin/forms.py
from django import forms
from chambres.models import Chambre, ChambreImage, ImageAccueil


class ChambreForm(forms.ModelForm):
    """Formulaire pour créer/modifier une chambre"""

    class Meta:
        model = Chambre
        fields = ['numero', 'type', 'prix', 'description', 'caracteristiques', 'disponible']
        widgets = {
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 101',
                'required': True
            }),
            'type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prix en Ar',
                'min': '0',
                'step': '1000',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description de la chambre...',
                'rows': 4,
                'required': True
            }),
            'caracteristiques': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: WiFi, Climatisation, TV...',
                'rows': 3,
                'required': True
            }),
            'disponible': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'numero': 'Numéro de chambre',
            'type': 'Type de chambre',
            'prix': 'Prix par nuit (Ar)',
            'description': 'Description',
            'caracteristiques': 'Caractéristiques',
            'disponible': 'Disponible'
        }

    def clean_numero(self):
        """Validation personnalisée du numéro"""
        numero = self.cleaned_data.get('numero')
        if not numero:
            raise forms.ValidationError("Le numéro de chambre est obligatoire.")

        # Vérifier l'unicité seulement si c'est une création ou si le numéro a changé
        if self.instance.pk:  # Modification
            if Chambre.objects.exclude(pk=self.instance.pk).filter(numero=numero).exists():
                raise forms.ValidationError(f"Une chambre avec le numéro {numero} existe déjà.")
        else:  # Création
            if Chambre.objects.filter(numero=numero).exists():
                raise forms.ValidationError(f"Une chambre avec le numéro {numero} existe déjà.")

        return numero

    def clean_prix(self):
        """Validation du prix"""
        prix = self.cleaned_data.get('prix')
        if prix and prix <= 0:
            raise forms.ValidationError("Le prix doit être supérieur à 0.")
        return prix


class ChambreImageForm(forms.ModelForm):
    """Formulaire pour ajouter des images à une chambre"""

    class Meta:
        model = ChambreImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

class ImageAccueilForm(forms.ModelForm):
    class Meta:
        model = ImageAccueil
        fields = ['image', 'description', 'actif']
        widgets = {
            'image': forms.FileInput(),
            'description': forms.TextInput(attrs={'placeholder': 'Description de la chambre...'}),
        }