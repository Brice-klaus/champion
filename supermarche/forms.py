"""
forms.py — Formulaires pour Le Champion Supermarché Togo
"""

from django import forms
from .models import CandidatureEmploi, MessageContact, Reservation
 

class ContactForm(forms.Form):
    """Formulaire de contact général."""

    SUJET_CHOICES = [
        ("",            "-- Choisir un sujet --"),
        ("info",        "Demande d'information"),
        ("reclamation", "Réclamation"),
        ("partenariat", "Proposition de partenariat"),
        ("emploi",      "Emploi"),
        ("presse",      "Presse / Médias"),
        ("autre",       "Autre"),
    ]

    prenom    = forms.CharField(max_length=100, label="Prénom")
    nom       = forms.CharField(max_length=100, label="Nom")
    email     = forms.EmailField(label="Adresse e-mail")
    telephone = forms.CharField(max_length=20, required=False, label="Téléphone")
    sujet     = forms.ChoiceField(choices=SUJET_CHOICES, label="Sujet")
    magasin   = forms.IntegerField(required=False, widget=forms.HiddenInput)
    message   = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5}),
        label="Votre message",
    )
    rgpd      = forms.BooleanField(
        label="J'accepte que mes données soient traitées pour répondre à ma demande.",
        error_messages={"required": "Vous devez accepter la politique de confidentialité."},
    )

    def clean_sujet(self):
        sujet = self.cleaned_data.get("sujet")
        if not sujet:
            raise forms.ValidationError("Veuillez choisir un sujet.")
        return sujet


class NewsletterForm(forms.Form):
    """Formulaire d'inscription à la newsletter."""

    prenom = forms.CharField(max_length=100, required=False, label="Prénom")
    email  = forms.EmailField(label="Adresse e-mail")
    rgpd   = forms.BooleanField(
        required=True,
        label="J'accepte de recevoir les offres et actualités du Champion.",
    )


class CandidatureForm(forms.ModelForm):
    """Formulaire de candidature à une offre d'emploi."""

    class Meta:
        model  = CandidatureEmploi
        fields = ["offre", "prenom", "nom", "email", "telephone", "cv", "lettre", "message"]
        widgets = {
            "offre":   forms.HiddenInput,
            "message": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "cv":      "CV (PDF recommandé)",
            "lettre":  "Lettre de motivation (facultatif)",
            "message": "Message complémentaire",
        }

    rgpd = forms.BooleanField(
        label="J'accepte que mes données soient utilisées dans le cadre de ce recrutement.",
        error_messages={"required": "Vous devez accepter la politique de confidentialité."},
    )


class RechercheForm(forms.Form):
    """Formulaire de recherche globale."""

    q = forms.CharField(
        max_length=150,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Rechercher un produit, une recette, une promo…",
            "autocomplete": "off",
        }),
    )
    
    
    





    
    
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            "client_nom", "client_telephone", "client_email",
            "type_recuperation", "magasin", "adresse_livraison",
            "creneau_souhaite", "note_client",
        ]
        widgets = {
            "client_nom": forms.TextInput(attrs={"class": "w-full rounded-xl border border-champion-100 dark:border-champion-700 bg-transparent px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-champion-500"}),
            "client_telephone": forms.TextInput(attrs={"class": "w-full rounded-xl border border-champion-100 dark:border-champion-700 bg-transparent px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-champion-500"}),
            "client_email": forms.EmailInput(attrs={"class": "w-full rounded-xl border border-champion-100 dark:border-champion-700 bg-transparent px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-champion-500"}),
            "type_recuperation": forms.RadioSelect,
            "magasin": forms.Select(attrs={"class": "w-full rounded-xl border border-champion-100 dark:border-champion-700 bg-transparent px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-champion-500"}),
            "adresse_livraison": forms.Textarea(attrs={"rows": 2, "class": "w-full rounded-xl border border-champion-100 dark:border-champion-700 bg-transparent px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-champion-500"}),
            "creneau_souhaite": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "type": "datetime-local",
                    "class": "w-full rounded-xl border border-champion-100 dark:border-champion-700 bg-transparent px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-champion-500",
                },
            ),
            "note_client": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-xl border border-champion-100 dark:border-champion-700 bg-transparent px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-champion-500"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["magasin"].required = False
        self.fields["adresse_livraison"].required = False
        self.fields["creneau_souhaite"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("type_recuperation") == "retrait" and not cleaned.get("magasin"):
            self.add_error("magasin", "Veuillez choisir un magasin pour le retrait.")
        if cleaned.get("type_recuperation") == "livraison" and not cleaned.get("adresse_livraison"):
            self.add_error("adresse_livraison", "Veuillez indiquer une adresse de livraison.")
        return cleaned