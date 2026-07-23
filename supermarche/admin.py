"""
admin.py — Interface d'administration pour Le Champion Supermarché Togo
"""
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from modeltranslation.admin import TranslationAdmin
from import_export.admin import ImportExportMixin

from .models import (
    ParametresSite, Ville, Magasin, ServiceMagasin,
    RayonCategorie, SousCategorie, Marque, Produit, ImageProduit,
    Promotion, CatalogueNumerique, CataloguePage,
    BanniereHero, BanniereSecondaire,
    Recette, TagArticle, Article,
    CarteFidelite, AvantagesFidelite,
    Departement, MembreEquipe, OffreEmploi, CandidatureEmploi,
    AvisClient, MessageContact, AbonneNewsletter,
    CategorieFAQ, QuestionFAQ,
    Partenaire, ChiffreCle,
    Reservation, LigneReservation,
)
from .resources import (
    ProduitResource, MagasinResource, PromotionResource,
    RayonCategorieResource, ArticleResource, RecetteResource,
    OffreEmploiResource,
)


# ── Inlines ──────────────────────────────────────────────

class CataloguePageInline(admin.TabularInline):
    model = CataloguePage
    extra = 1
    ordering = ["numero"]
    fields = ["numero", "image"]


class ServiceMagasinInline(admin.TabularInline):
    model = ServiceMagasin
    extra = 1


class SousCategorieInline(admin.TabularInline):
    model = SousCategorie
    extra = 1
    fields = ("nom", "slug", "ordre")


class ImageProduitInline(admin.TabularInline):
    model = ImageProduit
    extra = 1
    fields = ("image", "alt", "ordre")


class QuestionFAQInline(admin.TabularInline):
    model = QuestionFAQ
    extra = 1


class LigneReservationInline(admin.TabularInline):
    model = LigneReservation
    extra = 0
    readonly_fields = ["produit", "quantite", "prix_unitaire_capture"]


# ── Paramètres ───────────────────────────────────────────

@admin.register(ParametresSite)
class ParametresSiteAdmin(TranslationAdmin):
    fieldsets = (
        ("Identité", {"fields": ("nom_enseigne", "slogan", "description_courte", "logo", "favicon")}),
        ("Couleurs", {"fields": ("couleur_primaire", "couleur_secondaire")}),
        ("Contact", {"fields": ("email_contact", "telephone_principal", "google_maps_embed")}),
        ("Réseaux", {"fields": ("facebook_url", "instagram_url", "whatsapp_numero")}),
        ("Légal", {"fields": ("mentions_legales", "politique_confidentialite")}),
    )


# ── Magasins ─────────────────────────────────────────────

@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display = ("nom", "slug")
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Magasin)
class MagasinAdmin(ImportExportMixin, TranslationAdmin):
    resource_class = MagasinResource
    list_display = ("nom", "ville", "est_actif", "est_ouvert_24h", "ordre")
    list_filter = ("ville", "est_actif", "est_ouvert_24h")
    search_fields = ("nom", "adresse", "ville__nom")
    prepopulated_fields = {"slug": ("nom",)}
    readonly_fields = ("carte_interactive",)

    fieldsets = (
        (None, {"fields": ("nom", "slug", "ville", "adresse", "photo")}),
        ("Contact", {"fields": ("telephone", "email")}),
        ("Localisation", {
            "fields": ("carte_interactive", "latitude", "longitude"),
            "description": "Cliquez sur la carte ou déplacez le marqueur pour définir la position. "
                            "Les champs latitude/longitude se remplissent automatiquement.",
        }),
        ("Horaires & statut", {
            "fields": ("horaires", "est_ouvert_24h", "est_actif", "ordre", "date_ouverture")
        }),
    )

    class Media:
        css = {
            "all": (
                "https://api.mapbox.com/mapbox-gl-js/v3.6.0/mapbox-gl.css",
                "supermarche/css/magasin-map.css",
            )
        }
        js = (
            "https://api.mapbox.com/mapbox-gl-js/v3.6.0/mapbox-gl.js",
            "supermarche/js/magasin-map.js",
        )

    def carte_interactive(self, obj):
        lat = obj.latitude if obj.pk and obj.latitude else 6.1319
        lng = obj.longitude if obj.pk and obj.longitude else 1.2228
        return format_html(
            '<div id="magasin-map" data-lat="{}" data-lng="{}" '
            'data-token="{}" style="width:100%;height:560px;border-radius:8px;"></div>',
            lat, lng, settings.MAPBOX_ACCESS_TOKEN,
        )
    carte_interactive.short_description = "Localisation sur la carte"


# ── Catalogue ────────────────────────────────────────────

@admin.register(RayonCategorie)
class RayonCategorieAdmin(ImportExportMixin, TranslationAdmin):
    resource_class = RayonCategorieResource
    list_display = ("nom", "icone", "ordre", "est_visible")
    list_editable = ("ordre", "est_visible")
    inlines = [SousCategorieInline]
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Marque)
class MarqueAdmin(admin.ModelAdmin):
    list_display = ("nom", "est_locale")
    list_filter = ("est_locale",)
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(SousCategorie)
class SousCategorieAdmin(TranslationAdmin):
    list_display = ("nom", "slug", "ordre")
    list_filter = ("categorie",)
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Produit)
class ProduitAdmin(ImportExportMixin, TranslationAdmin):
    resource_class = ProduitResource
    list_display = ("nom", "sous_categorie", "prix_public", "est_en_promo",
                     "est_nouveau", "est_disponible", "est_visible")
    list_filter = ("est_en_promo", "est_nouveau", "est_local", "est_bio",
                   "est_visible", "est_disponible", "sous_categorie__categorie")
    search_fields = ("nom", "reference", "code_barre")
    list_editable = ("est_en_promo", "est_visible", "est_disponible")
    inlines = [ImageProduitInline]
    prepopulated_fields = {"slug": ("nom",)}
    fieldsets = (
        ("Identification", {"fields": ("nom", "slug", "reference", "code_barre")}),
        ("Classification", {"fields": ("sous_categorie", "marque")}),
        ("Description", {"fields": ("description", "composition", "contenance",
                                     "unite_de_vente", "conditionnement")}),
        ("Prix (FCFA)", {"fields": ("prix_public", "prix_promo", "est_en_promo")}),
        ("Média", {"fields": ("image_principale",)}),
        ("Flags", {"fields": ("est_nouveau", "est_coup_de_coeur", "est_local",
                               "est_bio", "est_visible", "est_disponible", "ordre")}),
    )


# ── Promotions & Catalogues ──────────────────────────────

@admin.register(Promotion)
class PromotionAdmin(ImportExportMixin, TranslationAdmin):
    resource_class = PromotionResource
    list_display = ("titre", "date_debut", "date_fin", "statut", "est_mis_en_avant")
    list_filter = ("statut", "est_mis_en_avant")
    filter_horizontal = ("produits", "magasins")
    prepopulated_fields = {"slug": ("titre",)}


@admin.register(CatalogueNumerique)
class CatalogueNumeriqueAdmin(TranslationAdmin):
    list_display = ["titre", "mois", "nb_pages", "est_actif", "created_at"]
    list_filter = ["est_actif", "mois"]
    inlines = [CataloguePageInline]
    actions = ["generer_pages_depuis_pdf"]

    @admin.action(description="Générer les pages (images) à partir du PDF")
    def generer_pages_depuis_pdf(self, request, queryset):
        from .generer_pages_catalogue import Command
        for catalogue in queryset:
            Command("generer_pages_catalogue", str(catalogue.pk))
        self.message_user(request, f"Pages générées pour {queryset.count()} catalogue(s).")


# ── Bannières ────────────────────────────────────────────

@admin.register(BanniereHero)
class BanniereHeroAdmin(TranslationAdmin):
    list_display = ("titre", "ordre", "est_actif", "date_debut", "date_fin")
    list_editable = ("ordre", "est_actif")


@admin.register(BanniereSecondaire)
class BanniereSecondaireAdmin(TranslationAdmin):
    list_display = ("titre", "position", "ordre", "est_actif")
    list_filter = ("position", "est_actif")
    list_editable = ("ordre", "est_actif")


# ── Recettes ─────────────────────────────────────────────

@admin.register(Recette)
class RecetteAdmin(ImportExportMixin, TranslationAdmin):
    resource_class = RecetteResource
    list_display = ("titre", "difficulte", "temps_preparation", "est_publiee", "est_mise_en_avant")
    list_filter = ("difficulte", "est_publiee", "est_mise_en_avant")
    search_fields = ("titre",)
    filter_horizontal = ("produits_lies",)
    prepopulated_fields = {"slug": ("titre",)}


# ── Articles ─────────────────────────────────────────────

@admin.register(TagArticle)
class TagArticleAdmin(TranslationAdmin):
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Article)
class ArticleAdmin(ImportExportMixin, TranslationAdmin):
    resource_class = ArticleResource
    list_display = ("titre", "type", "date_publication", "est_publie", "est_mis_en_avant")
    list_filter = ("type", "est_publie", "est_mis_en_avant")
    search_fields = ("titre", "chapeau")
    filter_horizontal = ("tags",)
    prepopulated_fields = {"slug": ("titre",)}
    date_hierarchy = "date_publication"


# ── Fidélité ─────────────────────────────────────────────

@admin.register(CarteFidelite)
class CarteFideliteAdmin(admin.ModelAdmin):
    list_display = ("numero_carte", "niveau", "points_cumules", "est_active")
    list_filter = ("niveau", "est_active")


@admin.register(AvantagesFidelite)
class AvantagesFideliteAdmin(TranslationAdmin):
    list_display = ("niveau", "titre", "ordre")
    list_editable = ("ordre",)
    list_filter = ("niveau",)


# ── Équipe & RH ──────────────────────────────────────────

@admin.register(Departement)
class DepartementAdmin(TranslationAdmin):
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(MembreEquipe)
class MembreEquipeAdmin(TranslationAdmin):
    list_display = ("nom_complet", "poste", "departement", "magasin", "est_visible", "ordre")
    list_filter = ("departement", "est_visible")
    list_editable = ("est_visible", "ordre")


@admin.register(OffreEmploi)
class OffreEmploiAdmin(ImportExportMixin, TranslationAdmin):
    resource_class = OffreEmploiResource
    list_display = ("titre", "departement", "magasin", "type_contrat", "statut", "date_limite")
    list_filter = ("statut", "type_contrat", "departement")
    search_fields = ("titre",)
    prepopulated_fields = {"slug": ("titre",)}


@admin.register(CandidatureEmploi)
class CandidatureEmploiAdmin(admin.ModelAdmin):
    list_display = ("prenom", "nom", "email", "offre", "est_traitee", "created_at")
    list_filter = ("est_traitee", "offre")
    search_fields = ("prenom", "nom", "email")
    readonly_fields = ("created_at",)


# ── Avis & Contact (pas de traduction : contenu généré par le client) ──

@admin.register(AvisClient)
class AvisClientAdmin(admin.ModelAdmin):
    list_display = ("prenom", "note", "magasin", "est_modere", "est_mis_en_avant", "created_at")
    list_filter = ("note", "est_modere", "est_mis_en_avant", "magasin")
    list_editable = ("est_modere", "est_mis_en_avant")


@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):
    list_display = ("prenom", "nom", "email", "sujet", "est_lu", "est_traite", "created_at")
    list_filter = ("sujet", "est_lu", "est_traite")
    search_fields = ("prenom", "nom", "email")
    readonly_fields = ("created_at",)


# ── Newsletter ───────────────────────────────────────────

@admin.register(AbonneNewsletter)
class AbonneNewsletterAdmin(admin.ModelAdmin):
    list_display = ("email", "prenom", "langue", "est_actif", "created_at")
    list_filter = ("langue", "est_actif")
    search_fields = ("email", "prenom")


# ── FAQ ──────────────────────────────────────────────────

@admin.register(CategorieFAQ)
class CategorieFAQAdmin(TranslationAdmin):
    inlines = [QuestionFAQInline]
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(QuestionFAQ)
class QuestionFAQAdmin(TranslationAdmin):
    list_display = ("question", "categorie", "ordre", "est_publie")
    list_filter = ("categorie", "est_publie")
    list_editable = ("ordre", "est_publie")


# ── Partenaires & Chiffres ───────────────────────────────

@admin.register(Partenaire)
class PartenaireAdmin(admin.ModelAdmin):
    list_display = ("nom", "type", "ordre", "est_actif")
    list_editable = ("ordre", "est_actif")
    list_filter = ("type", "est_actif")


@admin.register(ChiffreCle)
class ChiffreCleAdmin(TranslationAdmin):
    list_display = ("valeur", "libelle", "icone", "ordre", "est_actif")
    list_editable = ("ordre", "est_actif")


# ── Réservations ─────────────────────────────────────────

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ["numero", "client_nom", "client_telephone", "type_recuperation",
                     "statut", "creneau_souhaite", "cree_le"]
    list_filter = ["statut", "type_recuperation", "magasin"]
    search_fields = ["numero", "client_nom", "client_telephone"]
    readonly_fields = ["numero", "cree_le", "maj_le"]
    inlines = [LigneReservationInline]