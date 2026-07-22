from django.shortcuts import render

# Create your views here.
"""
=============================================================
  LE CHAMPION SUPERMARCHÉ TOGO — Views (Class-Based)
  Site Vitrine Moderne
=============================================================

Organisation des vues :
  1.  Mixin utilitaires
  2.  Accueil
  3.  Catalogue (catégories, sous-catégories, produits)
  4.  Promotions & Catalogues numériques
  5.  Recettes
  6.  Blog / Actualités
  7.  Magasins
  8.  Fidélité
  9.  Équipe & Carrières (offres + candidature)
  10. À propos
  11. Contact
  12. Newsletter
  13. FAQ
  14. Pages légales
  15. Recherche globale
"""

from django.views.generic import (
    TemplateView, ListView, DetailView,
    CreateView, FormView,
)
from django.views.generic.list import MultipleObjectMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.http import JsonResponse, Http404

from .models import (
    ParametresSite, Ville, Magasin,Marque,
    RayonCategorie, SousCategorie, Produit,
    Promotion, CatalogueNumerique,
    BanniereHero, BanniereSecondaire,
    Recette, TagArticle, Article,
    CarteFidelite, AvantagesFidelite,
    Departement, MembreEquipe, OffreEmploi, CandidatureEmploi,
    AvisClient, MessageContact, AbonneNewsletter,
    CategorieFAQ, QuestionFAQ,
    Partenaire, ChiffreCle,
)
from .forms import (
    ContactForm, NewsletterForm,
    CandidatureForm, RechercheForm,
)

from django.conf import settings
# ══════════════════════════════════════════════════════════════
# 1. MIXINS UTILITAIRES
# ══════════════════════════════════════════════════════════════

class ContextSiteMixin:
    """
    Injecte dans chaque vue les données globales du site :
    paramètres, catégories de navigation, bannières actives.
    """

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Paramètres globaux (singleton)
        ctx["parametres"] = ParametresSite.objects.first()

        # Navigation catalogue
        ctx["categories_nav"] = (
            RayonCategorie.objects
            .filter(est_visible=True)
            .prefetch_related("sous_categories")
            .order_by("ordre")
        )

        # Bannières secondaires actives (popup + accueil_milieu)
        ctx["bannieres_actives"] = (
            BanniereSecondaire.objects
            .filter(est_actif=True)
            .filter(
                Q(date_debut__isnull=True) | Q(date_debut__lte=today),
                Q(date_fin__isnull=True)   | Q(date_fin__gte=today),
            )
        )

        # Promotions en cours (pour le bandeau d'alerte)
        ctx["promotions_actives"] = (
            Promotion.objects
            .filter(statut="en_cours", est_mis_en_avant=True)[:3]
        )
        
        ctx["mapbox_token"] = settings.MAPBOX_ACCESS_TOKEN

        return ctx


# ══════════════════════════════════════════════════════════════
# 2. PAGE D'ACCUEIL
# ══════════════════════════════════════════════════════════════

class AccueilView(ContextSiteMixin, TemplateView):
    """
    Page d'accueil du site vitrine.
    Agrège hero slider, promotions, nouveautés,
    recettes mise en avant, avis clients.
    """
    template_name = "supermarche/index.html"

    def get_context_data(self, **kwargs):
        ctx  = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # ── Hero slider ──────────────────────────────────────
        ctx["hero_slides"] = (
            BanniereHero.objects
            .filter(est_actif=True)
            .filter(
                Q(date_debut__isnull=True) | Q(date_debut__lte=today),
                Q(date_fin__isnull=True)   | Q(date_fin__gte=today),
            )
            .order_by("ordre")
        )

        # ── Bannières secondaires accueil ────────────────────
        ctx["bannieres_milieu"] = (
            BanniereSecondaire.objects
            .filter(position="accueil_milieu", est_actif=True)
        )
        ctx["bannieres_bas"] = (
            BanniereSecondaire.objects
            .filter(position="accueil_bas", est_actif=True)
        )

        # ── Catégories mises en avant ────────────────────────
        ctx["categories_vedette"] = (
            RayonCategorie.objects
            .filter(est_visible=True)
            .order_by("ordre")[:8]
        )

        # ── Produits nouveautés ──────────────────────────────
        ctx["nouveautes"] = (
            Produit.objects
            .filter(est_nouveau=True, est_visible=True, est_disponible=True)
            .select_related("marque", "sous_categorie__categorie")
            .order_by("-created_at")[:8]
        )

        # ── Coups de cœur ────────────────────────────────────
        ctx["coups_de_coeur"] = (
            Produit.objects
            .filter(est_coup_de_coeur=True, est_visible=True, est_disponible=True)
            .select_related("marque")
            .order_by("-ordre")[:8]
        )
        # (la ligne print() supprimée)
        
        

        # ── Produits en promo ────────────────────────────────
        ctx["produits_promo"] = (
            Produit.objects
            .filter(est_en_promo=True, est_visible=True, est_disponible=True)
            .select_related("marque")
            .order_by("ordre")[:8]
        )

        # ── Promotions en cours ──────────────────────────────
        ctx["promotions_en_cours"] = (
            Promotion.objects
            .filter(statut="en_cours")
            .prefetch_related("produits", "magasins")
            .order_by("-est_mis_en_avant", "-date_debut")[:3]
        )

        # ── Recettes mises en avant ──────────────────────────
        ctx["recettes_vedette"] = (
            Recette.objects
            .filter(est_publiee=True, est_mise_en_avant=True)
            .order_by("-created_at")[:3]
        )

        # ── Dernier catalogue numérique ──────────────────────
        ctx["dernier_catalogue"] = (
            CatalogueNumerique.objects
            .filter(est_actif=True)
            .order_by("-mois")
            .first()
        )
        

        # ── Derniers articles ────────────────────────────────
        ctx["articles_recents"] = (
            Article.objects
            .filter(est_publie=True)
            .order_by("-date_publication")[:3]
        )

        # ── Avis clients mis en avant ────────────────────────
        ctx["temoignages"] = (
            AvisClient.objects
            .filter(est_modere=True, est_mis_en_avant=True)
            .order_by("-created_at")[:6]
        )

        # ── Chiffres clés ────────────────────────────────────
        ctx["chiffres_cles"] = (
            ChiffreCle.objects
            .filter(est_actif=True)
            .order_by("ordre")
        )

        # ── Partenaires ──────────────────────────────────────
        ctx["partenaires"] = (
            Partenaire.objects
            .filter(est_actif=True)
            .order_by("ordre")
        )

        # ── Produits locaux / made in Togo ───────────────────
        ctx["produits_locaux"] = (
            Produit.objects
            .filter(est_local=True, est_visible=True, est_disponible=True)
            .select_related("marque")
            .order_by("ordre")[:3]
        )
        
        
        # ── Tous nos Produits  ───────────────────
        ctx["produits"] = (
            Produit.objects
            .filter(est_visible=True, est_disponible=True)
            .select_related("marque")
            .order_by("ordre")[:8]
        )

        return ctx


# ══════════════════════════════════════════════════════════════
# 3. CATALOGUE PRODUITS
# ══════════════════════════════════════════════════════════════

# À ajouter dans supermarhe/views.py

# supermarhe/views.py

from django.views.generic import ListView, DetailView
from .models import CatalogueNumerique





class CatalogueDetailView(ContextSiteMixin, DetailView):
    model = CatalogueNumerique
    template_name = "supermarche/catalogue_detail.html"
    context_object_name = "catalogue"

    def get_queryset(self):
        return (
            CatalogueNumerique.objects
            .filter(est_actif=True)
            .prefetch_related("pages")
        )



class RayonCategorieView(ContextSiteMixin, TemplateView):
    """
    Page "Voir tous les rayons" : liste toutes les catégories
    avec leurs sous-catégories et un comptage de produits.
    """
    template_name = "supermarche/rayons_liste.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        categories = (
            RayonCategorie.objects
            .filter(est_visible=True)
            .prefetch_related("sous_categories")
            .annotate(nb_produits=Count(
                "sous_categories__produits",
                filter=Q(
                    sous_categories__produits__est_visible=True,
                    sous_categories__produits__est_disponible=True,
                )
            ))
            .order_by("ordre")
        )
        ctx["categories"] = categories
        ctx["nb_produits_total"] = sum(c.nb_produits for c in categories)

        ctx["breadcrumb"] = [
            {"label": "Catalogue", "url": None},
        ]
        return ctx

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.views.generic import DetailView


class RayonCategorieDetailView(ContextSiteMixin, DetailView):
    """
    Détail d'un rayon/catégorie : sous-catégories, produits filtrables,
    triables et paginés.
    """
    model = RayonCategorie
    template_name = "supermarche/rayoncategorie_detail.html"
    context_object_name = "categorie"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    TRI_CHOICES = {
        "pertinence": "ordre",
        "prix_asc": "prix_public",
        "prix_desc": "-prix_public",
        "nom": "nom",
        "recent": "-cree_le",
    }

    def get_queryset(self):
        return RayonCategorie.objects.filter(est_visible=True)

    def get_produits_queryset(self):
        categorie = self.object

        produits = (
            Produit.objects
            .filter(
                sous_categorie__categorie=categorie,
                est_visible=True,
            )
            .select_related("marque", "sous_categorie")
        )

        # Filtre sous-catégorie (optionnel, via ?sous_categorie=slug)
        sous_categorie_slug = self.request.GET.get("sous_categorie")
        if sous_categorie_slug:
            produits = produits.filter(sous_categorie__slug=sous_categorie_slug)

        # Filtre disponibilité (optionnel, via ?statut=disponible)
        statut = self.request.GET.get("statut")
        if statut == "disponible":
            produits = produits.filter(est_disponible=True)
        elif statut == "promo":
            produits = produits.filter(est_en_promo=True)

        # Tri
        tri = self.request.GET.get("tri", "pertinence")
        ordre = self.TRI_CHOICES.get(tri, "ordre")
        produits = produits.order_by(ordre)

        return produits

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        categorie = self.object

        # Sous-catégories avec comptage produits (pour les filtres latéraux)
        ctx["sous_categories"] = (
            categorie.sous_categories
            .annotate(nb_produits=Count(
                "produits",
                filter=Q(produits__est_visible=True, produits__est_disponible=True),
            ))
            .order_by("ordre")
        )

        # Pagination des produits, en préservant tri/statut/sous_categorie
        produits_qs = self.get_produits_queryset()
        paginator = Paginator(produits_qs, 24)
        page_number = self.request.GET.get("page")
        ctx["produits"] = paginator.get_page(page_number)

        ctx["tri_actuel"] = self.request.GET.get("tri", "pertinence")
        ctx["statut_actuel"] = self.request.GET.get("statut", "")
        ctx["sous_categorie_actuelle"] = self.request.GET.get("sous_categorie", "")

        # Query string sans "page", pour les liens de pagination
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["querystring_sans_page"] = params.urlencode()

        # Breadcrumb
        ctx["breadcrumb"] = [
            {"label": "Catalogue", "url": "supermarche:catalogue_accueil"},
            {"label": categorie.nom, "url": None},
        ]

        return ctx






class CategorieProduitView(ContextSiteMixin, ListView):
    """
    Liste des produits d'une catégorie (toutes sous-catégories confondues).
    Supporte le filtrage par sous-catégorie, marque, prix et flags.
    """
    template_name  = "supermarche/categorie.html"
    context_object_name = "produits"
    paginate_by    = 24

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.categorie = get_object_or_404(
            RayonCategorie, slug=kwargs["slug"], est_visible=True
        )

    def get_queryset(self):
        qs = (
            Produit.objects
            .filter(
                sous_categorie__categorie=self.categorie,
                est_visible=True,
                est_disponible=True,
            )
            .select_related("marque", "sous_categorie")
        )

        # Filtre sous-catégorie
        sc_slug = self.request.GET.get("sous_categorie")
        if sc_slug:
            qs = qs.filter(sous_categorie__slug=sc_slug)

        # Filtre marque
        marque_slug = self.request.GET.get("marque")
        if marque_slug:
            qs = qs.filter(marque__slug=marque_slug)

        # Filtre flags
        if self.request.GET.get("promo"):
            qs = qs.filter(est_en_promo=True)
        if self.request.GET.get("nouveau"):
            qs = qs.filter(est_nouveau=True)
        if self.request.GET.get("local"):
            qs = qs.filter(est_local=True)
        if self.request.GET.get("bio"):
            qs = qs.filter(est_bio=True)

        # Filtre fourchette de prix
        prix_min = self.request.GET.get("prix_min")
        prix_max = self.request.GET.get("prix_max")
        if prix_min:
            qs = qs.filter(prix_public__gte=prix_min)
        if prix_max:
            qs = qs.filter(prix_public__lte=prix_max)

        # Tri
        tri = self.request.GET.get("tri", "ordre")
        TRI_MAP = {
            "ordre":       "ordre",
            "nom_asc":     "nom",
            "nom_desc":    "-nom",
            "prix_asc":    "prix_public",
            "prix_desc":   "-prix_public",
            "nouveaute":   "-created_at",
        }
        qs = qs.order_by(TRI_MAP.get(tri, "ordre"))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categorie"]      = self.categorie
        ctx["sous_categories"] = self.categorie.sous_categories.all()
        ctx["marques"] = (
            Produit.objects
            .filter(sous_categorie__categorie=self.categorie, est_visible=True)
            .values_list("marque__nom", "marque__slug")
            .exclude(marque__isnull=True)
            .distinct()
        )
        ctx["filtres_actifs"] = {
            k: v for k, v in self.request.GET.items()
            if k not in ("page",) and v
        }
        return ctx





class ProduitDetailView(ContextSiteMixin, DetailView):
    """
    Fiche produit complète :
    galerie, description, composition, produits similaires.
    """
    model               = Produit
    template_name       = "supermarche/produit_detail.html"
    context_object_name = "produit"
    slug_field          = "slug"
    slug_url_kwarg      = "slug"

    def get_queryset(self):
        return (
            Produit.objects
            .filter(est_visible=True)
            .select_related("marque", "sous_categorie__categorie")
            .prefetch_related("images_galerie", "promotions", "recettes")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        produit = self.object

        # Produits similaires (même sous-catégorie, hors produit courant)
        ctx["produits_similaires"] = (
            Produit.objects
            .filter(
                sous_categorie=produit.sous_categorie,
                est_visible=True,
                est_disponible=True,
            )
            .exclude(pk=produit.pk)
            .select_related("marque")
            .order_by("ordre")[:6]
        )

        # Promotions liées au produit
        ctx["promotions_produit"] = (
            produit.promotions.filter(statut="en_cours")
        )

        # Recettes utilisant ce produit
        ctx["recettes_associees"] = (
            produit.recettes.filter(est_publiee=True)[:3]
        )

        # Breadcrumb
        if produit.sous_categorie:
            ctx["breadcrumb"] = [
                {"label": "Catalogue",             "url": "catalogue_accueil"},
                {"label": produit.sous_categorie.categorie.nom,
                 "url": None},
                {"label": produit.sous_categorie.nom, "url": None},
                {"label": produit.nom,              "url": None},
            ]
        return ctx


class ProduitFiltreMixin:
    """
    Mixin factorisant la logique de filtres (marque, sous-catégorie,
    prix, badges, tri) commune à toutes les vues de listing produits.
    Chaque vue fille définit `filtre_base` pour restreindre le queryset
    de départ (nouveautés, locaux, coups de cœur, promo, ou aucun filtre).
    """
    paginate_by = 24
    context_object_name = "produits"

    filtre_base = {}  # ex: {"est_nouveau": True} — surchargé par vue fille

    def get_base_queryset(self):
        return (
            Produit.objects
            .filter(est_visible=True, **self.filtre_base)
            .select_related("marque", "sous_categorie__categorie")
        )

    def get_queryset(self):
        qs = self.get_base_queryset()

        marque_slug = self.request.GET.get("marque")
        if marque_slug:
            qs = qs.filter(marque__slug=marque_slug)

        sous_categorie_slug = self.request.GET.get("sous_categorie")
        if sous_categorie_slug:
            qs = qs.filter(sous_categorie__slug=sous_categorie_slug)

        if self.request.GET.get("bio") == "1":
            qs = qs.filter(est_bio=True)
        if self.request.GET.get("local") == "1":
            qs = qs.filter(est_local=True)
        if self.request.GET.get("disponible") == "1":
            qs = qs.filter(est_disponible=True)

        prix_min = self.request.GET.get("prix_min")
        prix_max = self.request.GET.get("prix_max")
        if prix_min:
            qs = qs.filter(prix_public__gte=prix_min)
        if prix_max:
            qs = qs.filter(prix_public__lte=prix_max)

        tri = self.request.GET.get("tri", "pertinence")
        ordres = {
            "pertinence": "ordre",
            "prix_asc": "prix_public",
            "prix_desc": "-prix_public",
            "recent": "-created_at",
            "nom": "nom",
        }
        return qs.order_by(ordres.get(tri, "ordre"))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        base_qs = self.get_base_queryset()

        ctx["marques"] = (
            Marque.objects
            .filter(produits__in=base_qs)
            .distinct()
            .order_by("nom")
        )
        ctx["sous_categories"] = (
            SousCategorie.objects
            .filter(produits__in=base_qs)
            .distinct()
            .order_by("nom")
        )

        ctx["marque_actuelle"] = self.request.GET.get("marque", "")
        ctx["sous_categorie_actuelle"] = self.request.GET.get("sous_categorie", "")
        ctx["bio_actif"] = self.request.GET.get("bio") == "1"
        ctx["local_actif"] = self.request.GET.get("local") == "1"
        ctx["disponible_actif"] = self.request.GET.get("disponible") == "1"
        ctx["prix_min_actuel"] = self.request.GET.get("prix_min", "")
        ctx["prix_max_actuel"] = self.request.GET.get("prix_max", "")
        ctx["tri_actuel"] = self.request.GET.get("tri", "pertinence")

        params = self.request.GET.copy()
        params.pop("page", None)
        ctx["querystring_sans_page"] = params.urlencode()

        return ctx

class ProduitsPromoView(ProduitFiltreMixin, ContextSiteMixin, ListView):
    """Tous les produits actuellement en promotion."""
    template_name = "supermarche/produits_promo.html"
    filtre_base = {"est_en_promo": True}





class ProduitsNouveautesView(ProduitFiltreMixin, ContextSiteMixin, ListView):
    """Produits marqués nouveauté."""
    template_name = "supermarche/nouveautes.html"
    filtre_base = {"est_nouveau": True}


class ProduitsLocauxView(ProduitFiltreMixin, ContextSiteMixin, ListView):
    """Produits made in Togo mis en avant."""
    template_name = "supermarche/produits_locaux.html"
    filtre_base = {"est_local": True}


class ProduitsCoupsDeCoeurView(ProduitFiltreMixin, ContextSiteMixin, ListView):
    """Sélection coups de cœur de l'équipe."""
    template_name = "supermarche/produits_coups_de_coeur.html"
    filtre_base = {"est_coup_de_coeur": True}
    
    
class ProduitsTousView(ProduitFiltreMixin, ContextSiteMixin, ListView):
    """Catalogue complet, sans filtre de base."""
    template_name = "supermarche/produits_tous.html"
    filtre_base = {}

# ══════════════════════════════════════════════════════════════
# 4. PROMOTIONS & CATALOGUES NUMÉRIQUES
# ══════════════════════════════════════════════════════════════

class PromotionsListView(ContextSiteMixin, ListView):
    """
    Liste de toutes les opérations promotionnelles
    (en cours, planifiées, terminées).
    """
    template_name       = "supermarche/promotions_liste.html"
    context_object_name = "promotions"
    paginate_by         = 9

    def get_queryset(self):
        qs = Promotion.objects.all()
        statut = self.request.GET.get("statut")
        if statut in ("en_cours", "planifiee", "terminee"):
            qs = qs.filter(statut=statut)
        return qs.order_by("-date_debut")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["statut_actif"] = self.request.GET.get("statut", "")
        ctx["promotions_en_cours_count"] = (
            Promotion.objects.filter(statut="en_cours").count()
        )
        return ctx


class PromotionDetailView(ContextSiteMixin, DetailView):
    """Détail d'une opération promotionnelle avec ses produits."""
    model               = Promotion
    template_name       = "supermarche/promotions_detail.html"
    context_object_name = "promotion"
    slug_field          = "slug"
    slug_url_kwarg      = "slug"

    def get_queryset(self):
        return (
            Promotion.objects
            .prefetch_related("produits__marque", "magasins")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["autres_promotions"] = (
            Promotion.objects
            .filter(statut="en_cours")
            .exclude(pk=self.object.pk)[:3]
        )
        return ctx



class CataloguesNumeriquesView(ContextSiteMixin, ListView):
    """
    Archive des catalogues PDF téléchargeables.
    """
    template_name       = "supermarche/catalogues_liste.html"
    context_object_name = "catalogues"
    paginate_by         = 12

    def get_queryset(self):
        return (
            CatalogueNumerique.objects
            .filter(est_actif=True)
            .order_by("-mois")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["catalogue_actuel"] = (
            CatalogueNumerique.objects.filter(est_actif=True).first()
        )
        return ctx


# ══════════════════════════════════════════════════════════════
# 5. RECETTES
# ══════════════════════════════════════════════════════════════

class RecetteListView(ContextSiteMixin, ListView):
    """
    Liste des recettes avec filtres difficulté et temps.
    """
    template_name       = "supermarche/recettes/liste.html"
    context_object_name = "recettes"
    paginate_by         = 9

    def get_queryset(self):
        qs = Recette.objects.filter(est_publiee=True).order_by("-created_at")

        difficulte = self.request.GET.get("difficulte")
        if difficulte in ("1", "2", "3"):
            qs = qs.filter(difficulte=difficulte)

        temps_max = self.request.GET.get("temps_max")
        if temps_max:
            qs = [
                r for r in qs
                if (r.temps_preparation + r.temps_cuisson) <= int(temps_max)
            ]

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recettes_vedette"] = (
            Recette.objects
            .filter(est_publiee=True, est_mise_en_avant=True)[:3]
        )
        return ctx


class RecetteDetailView(ContextSiteMixin, DetailView):
    """
    Fiche recette complète : ingrédients, étapes,
    produits associés, recettes similaires.
    """
    model               = Recette
    template_name       = "supermarche/recettes/detail.html"
    context_object_name = "recette"
    slug_field          = "slug"
    slug_url_kwarg      = "slug"

    def get_queryset(self):
        return (
            Recette.objects
            .filter(est_publiee=True)
            .prefetch_related("produits_lies__marque")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recettes_similaires"] = (
            Recette.objects
            .filter(est_publiee=True, difficulte=self.object.difficulte)
            .exclude(pk=self.object.pk)[:4]
        )
        return ctx


# ══════════════════════════════════════════════════════════════
# 6. BLOG / ACTUALITÉS
# ══════════════════════════════════════════════════════════════

class ArticleListView(ContextSiteMixin, ListView):
    """
    Liste des articles publiés avec filtres par type et tag.
    """
    template_name       = "supermarche/blog/liste.html"
    context_object_name = "articles"
    paginate_by         = 9

    def get_queryset(self):
        qs = (
            Article.objects
            .filter(est_publie=True)
            .prefetch_related("tags")
            .order_by("-date_publication")
        )

        type_filtre = self.request.GET.get("type")
        if type_filtre:
            qs = qs.filter(type=type_filtre)

        tag_slug = self.kwargs.get("tag_slug")
        if tag_slug:
            self.tag_actif = get_object_or_404(TagArticle, slug=tag_slug)
            qs = qs.filter(tags=self.tag_actif)
        else:
            self.tag_actif = None

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tags"]            = TagArticle.objects.all()
        ctx["tag_actif"]       = self.tag_actif
        ctx["type_actif"]      = self.request.GET.get("type", "")
        ctx["article_vedette"] = (
            Article.objects
            .filter(est_publie=True, est_mis_en_avant=True)
            .order_by("-date_publication")
            .first()
        )
        ctx["types_article"]   = Article.TYPE_CHOICES
        return ctx


class ArticleDetailView(ContextSiteMixin, DetailView):
    """
    Article complet avec articles liés.
    """
    model               = Article
    template_name       = "supermarche/blog/detail.html"
    context_object_name = "article"
    slug_field          = "slug"
    slug_url_kwarg      = "slug"

    def get_queryset(self):
        return (
            Article.objects
            .filter(est_publie=True)
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object
        ctx["articles_recents"] = (
            Article.objects
            .filter(est_publie=True)
            .exclude(pk=article.pk)
            .order_by("-date_publication")[:4]
        )
        ctx["articles_meme_type"] = (
            Article.objects
            .filter(est_publie=True, type=article.type)
            .exclude(pk=article.pk)[:3]
        )
        return ctx


# ══════════════════════════════════════════════════════════════
# 7. MAGASINS
# ══════════════════════════════════════════════════════════════
import json
from django.core.serializers.json import DjangoJSONEncoder

class MagasinListView(ContextSiteMixin, ListView):
    template_name       = "supermarche/magasinsliste.html"
    context_object_name = "magasins"

    def get_queryset(self):
        qs = (
            Magasin.objects
            .filter(est_actif=True)
            .select_related("ville")
            .prefetch_related("services")
            .order_by("ordre", "nom")
        )
        ville_slug = self.request.GET.get("ville")
        if ville_slug:
            qs = qs.filter(ville__slug=ville_slug)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["villes"]      = Ville.objects.filter(magasins__est_actif=True).distinct()
        ctx["ville_active"] = self.request.GET.get("ville", "")
        ctx["nb_magasins"] = Magasin.objects.filter(est_actif=True).count()

        ctx["magasins_json"] = json.dumps([
            {
                "id": m.pk,
                "nom": m.nom,
                "adresse": m.adresse,
                "lat": float(m.latitude) if m.latitude else None,
                "lng": float(m.longitude) if m.longitude else None,
            }
            for m in ctx["magasins"] if m.latitude and m.longitude
        ], cls=DjangoJSONEncoder)

        return ctx

class MagasinDetailView(ContextSiteMixin, DetailView):
    """
    Fiche d'un magasin : horaires, services, équipe, promotions locales.
    """
    model               = Magasin
    template_name       = "supermarche/magasinsdetail.html"
    context_object_name = "magasin"
    slug_field          = "slug"
    slug_url_kwarg      = "slug"

    def get_queryset(self):
        return (
            Magasin.objects
            .filter(est_actif=True)
            .select_related("ville")
            .prefetch_related("services", "equipe", "promotions", "avis")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        magasin = self.object

        ctx["avis_magasin"] = (
            AvisClient.objects
            .filter(magasin=magasin, est_modere=True)
            .order_by("-created_at")[:5]
        )
        ctx["note_moyenne"] = (
            AvisClient.objects
            .filter(magasin=magasin, est_modere=True)
            .aggregate(moy=Avg("note"))["moy"]
        )
        ctx["promotions_locales"] = (
            Promotion.objects
            .filter(statut="en_cours")
            .filter(Q(magasins=magasin) | Q(magasins__isnull=True))
            .distinct()[:3]
        )
        ctx["equipe_visible"] = (
            magasin.equipe.filter(est_visible=True).order_by("ordre")
        )
        ctx["autres_magasins"] = (
            Magasin.objects
            .filter(est_actif=True)
            .exclude(pk=magasin.pk)
            .select_related("ville")[:4]
        )
        return ctx


# ══════════════════════════════════════════════════════════════
# 8. FIDÉLITÉ — CHAMPION CLUB
# ══════════════════════════════════════════════════════════════

class FideliteView(ContextSiteMixin, TemplateView):
    """
    Page programme de fidélité Champion Club :
    présentation des niveaux et avantages.
    """
    template_name = "supermarche/fidelite/programme.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        niveaux = [n[0] for n in CarteFidelite.NIVEAU_CHOICES]
        avantages_par_niveau = {}
        for niveau in niveaux:
            avantages_par_niveau[niveau] = (
                AvantagesFidelite.objects
                .filter(niveau=niveau)
                .order_by("ordre")
            )

        ctx["niveaux"]              = CarteFidelite.NIVEAU_CHOICES
        ctx["avantages_par_niveau"] = avantages_par_niveau
        ctx["newsletter_form"]      = NewsletterForm()
        return ctx


# ══════════════════════════════════════════════════════════════
# 9. ÉQUIPE & CARRIÈRES
# ══════════════════════════════════════════════════════════════

class AProposView(ContextSiteMixin, TemplateView):
    """
    Page À propos : histoire, valeurs, chiffres clés,
    membres de l'équipe, partenaires.
    """
    template_name = "supermarche/a_propos.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["chiffres_cles"] = (
            ChiffreCle.objects.filter(est_actif=True).order_by("ordre")
        )
        ctx["equipe"] = (
            MembreEquipe.objects
            .filter(est_visible=True)
            .select_related("departement", "magasin")
            .order_by("ordre")
        )
        ctx["partenaires"] = (
            Partenaire.objects.filter(est_actif=True).order_by("ordre")
        )
        ctx["temoignages"] = (
            AvisClient.objects
            .filter(est_modere=True, est_mis_en_avant=True)
            .order_by("-created_at")[:3]
        )
        return ctx


class CarrieresView(ContextSiteMixin, ListView):
    """
    Page Carrières : offres d'emploi ouvertes,
    filtrables par département, ville et type de contrat.
    """
    template_name       = "supermarche/carrieres/liste.html"
    context_object_name = "offres"
    paginate_by         = 10

    def get_queryset(self):
        qs = (
            OffreEmploi.objects
            .filter(statut="ouverte")
            .select_related("departement", "magasin__ville")
            .order_by("-date_publication")
        )

        dept = self.request.GET.get("departement")
        if dept:
            qs = qs.filter(departement__slug=dept)

        contrat = self.request.GET.get("contrat")
        if contrat:
            qs = qs.filter(type_contrat=contrat)

        ville = self.request.GET.get("ville")
        if ville:
            qs = qs.filter(magasin__ville__slug=ville)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["departements"]   = Departement.objects.all()
        ctx["types_contrat"]  = OffreEmploi.TYPE_CONTRAT_CHOICES
        ctx["villes"]         = Ville.objects.filter(magasins__est_actif=True).distinct()
        ctx["nb_offres"]      = OffreEmploi.objects.filter(statut="ouverte").count()
        ctx["filtres_actifs"] = {
            k: v for k, v in self.request.GET.items() if v
        }
        return ctx


class OffreEmploiDetailView(ContextSiteMixin, DetailView):
    """
    Détail d'une offre d'emploi avec formulaire de candidature intégré.
    """
    model               = OffreEmploi
    template_name       = "supermarche/carrieres/offre_detail.html"
    context_object_name = "offre"
    slug_field          = "slug"
    slug_url_kwarg      = "slug"

    def get_queryset(self):
        return (
            OffreEmploi.objects
            .filter(statut="ouverte")
            .select_related("departement", "magasin__ville")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["candidature_form"] = CandidatureForm(
            initial={"offre": self.object}
        )
        ctx["offres_similaires"] = (
            OffreEmploi.objects
            .filter(statut="ouverte", departement=self.object.departement)
            .exclude(pk=self.object.pk)[:3]
        )
        return ctx


class CandidatureCreateView(ContextSiteMixin, CreateView):
    """
    Traitement du formulaire de candidature à une offre.
    Redirige vers la page de confirmation après succès.
    """
    model         = CandidatureEmploi
    form_class    = CandidatureForm
    template_name = "supermarche/carrieres/candidature_form.html"
    success_url   = reverse_lazy("candidature_confirmation")

    def form_valid(self, form):
        messages.success(
            self.request,
            "✅ Votre candidature a bien été envoyée. "
            "Nous vous contacterons dans les meilleurs délais."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "⚠️ Veuillez corriger les erreurs du formulaire."
        )
        return super().form_invalid(form)


class CandidatureConfirmationView(ContextSiteMixin, TemplateView):
    """Page de confirmation après envoi de candidature."""
    template_name = "supermarche/carrieres/candidature_confirmation.html"


# ══════════════════════════════════════════════════════════════
# 10. CONTACT
# ══════════════════════════════════════════════════════════════

class ContactView(ContextSiteMixin, FormView):
    """
    Page de contact avec formulaire.
    Sauvegarde le message en base et affiche une confirmation.
    """
    template_name = "supermarche/contact.html"
    form_class    = ContactForm
    success_url   = reverse_lazy("contact_confirmation")

    def form_valid(self, form):
        # Sauvegarde en base
        msg = MessageContact(
            prenom    = form.cleaned_data["prenom"],
            nom       = form.cleaned_data["nom"],
            email     = form.cleaned_data["email"],
            telephone = form.cleaned_data.get("telephone", ""),
            sujet     = form.cleaned_data["sujet"],
            message   = form.cleaned_data["message"],
        )
        magasin_id = form.cleaned_data.get("magasin")
        if magasin_id:
            msg.magasin_id = magasin_id
        msg.save()

        messages.success(
            self.request,
            "✅ Votre message a bien été envoyé. "
            "Nous vous répondrons sous 48h."
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["magasins"] = Magasin.objects.filter(est_actif=True).select_related("ville")
        return ctx


class ContactConfirmationView(ContextSiteMixin, TemplateView):
    """Page de confirmation après envoi du formulaire de contact."""
    template_name = "supermarche/contact_confirmation.html"


# ══════════════════════════════════════════════════════════════
# 11. NEWSLETTER
# ══════════════════════════════════════════════════════════════

class NewsletterInscriptionView(FormView):
    """
    Vue AJAX-friendly pour l'inscription à la newsletter.
    Répond JSON si la requête est AJAX, sinon redirige.
    """
    form_class  = NewsletterForm
    success_url = reverse_lazy("accueil")

    def form_valid(self, form):
        email  = form.cleaned_data["email"]
        prenom = form.cleaned_data.get("prenom", "")

        abonne, created = AbonneNewsletter.objects.get_or_create(
            email=email,
            defaults={"prenom": prenom, "est_actif": True},
        )
        if not created and not abonne.est_actif:
            abonne.est_actif = True
            abonne.save(update_fields=["est_actif"])

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "message": "Merci ! Vous êtes inscrit(e) à notre newsletter.",
            })

        messages.success(self.request, "✅ Inscription à la newsletter réussie !")
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        return redirect(reverse_lazy("accueil"))


class NewsletterDesinscriptionView(TemplateView):
    """
    Désinscription via le lien tokenisé envoyé par email.
    """
    template_name = "supermarche/newsletter/desinscription.html"

    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")
        try:
            abonne = AbonneNewsletter.objects.get(token_desinscription=token)
            abonne.est_actif = False
            abonne.save(update_fields=["est_actif"])
            self.desincrit = True
        except AbonneNewsletter.DoesNotExist:
            self.desincrit = False
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["desincrit"] = getattr(self, "desincrit", False)
        return ctx


# ══════════════════════════════════════════════════════════════
# 12. FAQ
# ══════════════════════════════════════════════════════════════

class FAQView(ContextSiteMixin, TemplateView):
    """
    Page FAQ complète, organisée par catégorie.
    """
    template_name = "supermarche/faq.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories_faq"] = (
            CategorieFAQ.objects
            .prefetch_related(
                models_prefetch("questions",
                    queryset=QuestionFAQ.objects.filter(est_publie=True).order_by("ordre"))
            )
            .order_by("ordre")
        )
        return ctx


# ══════════════════════════════════════════════════════════════
# 13. PAGES LÉGALES
# ══════════════════════════════════════════════════════════════

class MentionsLegalesView(ContextSiteMixin, TemplateView):
    """Mentions légales — données issues de ParametresSite."""
    template_name = "supermarche/legal/mentions_legales.html"


class PolitiqueConfidentialiteView(ContextSiteMixin, TemplateView):
    """Politique de confidentialité (RGPD)."""
    template_name = "supermarche/legal/politique_confidentialite.html"


# ══════════════════════════════════════════════════════════════
# 14. RECHERCHE GLOBALE
# ══════════════════════════════════════════════════════════════

 

class RechercheView(ContextSiteMixin, TemplateView):
    """
    Recherche globale multi-modèles :
    produits, recettes, articles, promotions.
    """
    template_name = "supermarche/recherche.html"

    NB_PRODUITS   = 12
    NB_RECETTES   = 6
    NB_ARTICLES   = 6
    NB_PROMOTIONS = 4

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        ctx["query"] = query
        ctx["form"] = RechercheForm(initial={"q": query})

        if not query:
            ctx["total_resultats"] = 0
            return ctx

        produits_qs = (
            Produit.objects
            .filter(
                Q(nom__icontains=query) |
                Q(description__icontains=query) |
                Q(marque__nom__icontains=query),
                est_visible=True,
            )
            .select_related("marque", "sous_categorie__categorie")
        )
        recettes_qs = Recette.objects.filter(
            Q(titre__icontains=query) | Q(description__icontains=query),
            est_publiee=True,
        )
        articles_qs = Article.objects.filter(
            Q(titre__icontains=query) | Q(chapeau__icontains=query),
            est_publie=True,
        )
        promotions_qs = Promotion.objects.filter(
            Q(titre__icontains=query) | Q(description__icontains=query),
            statut="en_cours",
        )

        # Comptes réels (avant troncature) pour un total exact
        nb_produits   = produits_qs.count()
        nb_recettes   = recettes_qs.count()
        nb_articles   = articles_qs.count()
        nb_promotions = promotions_qs.count()

        ctx["produits"]   = produits_qs[: self.NB_PRODUITS]
        ctx["recettes"]   = recettes_qs[: self.NB_RECETTES]
        ctx["articles"]   = articles_qs[: self.NB_ARTICLES]
        ctx["promotions"] = promotions_qs[: self.NB_PROMOTIONS]

        ctx["nb_produits"]   = nb_produits
        ctx["nb_recettes"]   = nb_recettes
        ctx["nb_articles"]   = nb_articles
        ctx["nb_promotions"] = nb_promotions
        ctx["total_resultats"] = nb_produits + nb_recettes + nb_articles + nb_promotions

        return ctx
# ══════════════════════════════════════════════════════════════
# 15. VUE D'ERREURS PERSONNALISÉES
# ══════════════════════════════════════════════════════════════

def page_404(request, exception=None):
    """Page 404 personnalisée."""
    from django.shortcuts import render
    return render(request, "supermarche/errors/404.html", status=404)


def page_500(request):
    """Page 500 personnalisée."""
    from django.shortcuts import render
    return render(request, "supermarche/errors/500.html", status=500)


# ── Import utilitaire interne ─────────────────────────────────
# Alias pour Prefetch dans la vue FAQ
from django.db.models import Prefetch as models_prefetch




from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, FormView

from .forms import ReservationForm
from .models import LigneReservation, Magasin, Produit, Reservation
from .panier import Panier


class PanierAjouterView(ContextSiteMixin, View):
    def post(self, request, produit_id):
        produit = get_object_or_404(Produit, pk=produit_id, est_visible=True)
        quantite = int(request.POST.get("quantite", 1))
        panier = Panier(request)
        panier.ajouter(produit, quantite)
        messages.success(request, f"{produit.nom} ajouté au panier.")
        return redirect(request.POST.get("next", "supermarche:panier"))


class PanierRetirerView(ContextSiteMixin, View):
    def post(self, request, produit_id):
        Panier(request).retirer(produit_id)
        return redirect("supermarche:panier")

class PanierModifierView(View):
    def post(self, request, produit_id):
        quantite = int(request.POST.get("quantite", 1))
        Panier(request).modifier_quantite(produit_id, quantite)
        return redirect(request.POST.get("next", "supermarche:panier"))

class PanierView(ContextSiteMixin, TemplateView):
    template_name = "supermarche/panier.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["panier"] = Panier(self.request)
        return ctx

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class ReservationCreateView(ContextSiteMixin, FormView):
    template_name = "supermarche/reservation_form.html"
    form_class = ReservationForm

    def dispatch(self, request, *args, **kwargs):
        self.panier = Panier(request)
        if len(self.panier) == 0:
            messages.warning(request, "Votre panier est vide.")
            return redirect("supermarche:panier")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["panier"] = self.panier
        ctx["magasins"] = Magasin.objects.all()
        return ctx

    def form_valid(self, form):
        reservation = form.save()
        for item in self.panier:
            LigneReservation.objects.create(
                reservation=reservation,
                produit=item["produit"],
                quantite=item["quantite"],
                prix_unitaire_capture=item["produit"].prix_affiche,
            )
        self.panier.vider()
        self._envoyer_email_confirmation(reservation)
        return redirect(reservation.get_absolute_url())

    def _envoyer_email_confirmation(self, reservation):
        if not reservation.client_email:
            return

        contexte = {"reservation": reservation}
        try:
            corps_html = render_to_string("supermarche/emails/reservation_confirmation.html", contexte)
            corps_texte = render_to_string("supermarche/emails/reservation_confirmation.txt", contexte)
            send_mail(
                subject=f"Réservation confirmée — {reservation.numero}",
                message=corps_texte,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reservation.client_email],
                html_message=corps_html,
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                "Échec de l'envoi de l'email de confirmation pour la réservation %s",
                reservation.numero,
            )

class ReservationConfirmationView(ContextSiteMixin, DetailView):
    model = Reservation
    template_name = "supermarche/reservation_confirmation.html"
    context_object_name = "reservation"
    slug_field = "numero"
    slug_url_kwarg = "numero"

    def get_object(self):
        return get_object_or_404(Reservation, numero=self.kwargs["numero"])