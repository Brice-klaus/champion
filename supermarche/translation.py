"""
=============================================================
  LE CHAMPION SUPERMARCHÉ TOGO — Traductions des modèles
  Enregistrement django-modeltranslation
=============================================================
"""

from modeltranslation.translator import register, TranslationOptions

from .models import (
    ParametresSite,
    Magasin,
    ServiceMagasin,
    RayonCategorie,
    SousCategorie,
    Produit,
    Promotion,
    CatalogueNumerique,
    BanniereHero,
    BanniereSecondaire,
    Recette,
    TagArticle,
    Article,
    Departement,
    MembreEquipe,
    OffreEmploi,
    AvantagesFidelite,
    CategorieFAQ,
    QuestionFAQ,
    ChiffreCle,
)


# ──────────────────────────────────────────────────────────
# 1. PARAMÈTRES GÉNÉRAUX DU SITE
# ──────────────────────────────────────────────────────────

@register(ParametresSite)
class ParametresSiteTranslationOptions(TranslationOptions):
    fields = ("slogan", "description_courte", "mentions_legales", "politique_confidentialite")


# ──────────────────────────────────────────────────────────
# 2. MAGASINS
# ──────────────────────────────────────────────────────────
# Ville et Magasin.nom/adresse ne sont PAS traduits : noms propres et
# adresses restent identiques quelle que soit la langue.

@register(Magasin)
class MagasinTranslationOptions(TranslationOptions):
    fields = ("horaires",)


@register(ServiceMagasin)
class ServiceMagasinTranslationOptions(TranslationOptions):
    fields = ("libelle",)


# ──────────────────────────────────────────────────────────
# 3. CATALOGUE PRODUITS
# ──────────────────────────────────────────────────────────
# Marque.nom n'est pas traduit : un nom de marque reste identique.

@register(RayonCategorie)
class RayonCategorieTranslationOptions(TranslationOptions):
    fields = ("nom", "description")


@register(SousCategorie)
class SousCategorieTranslationOptions(TranslationOptions):
    fields = ("nom",)


@register(Produit)
class ProduitTranslationOptions(TranslationOptions):
    fields = ("nom", "description", "composition", "conditionnement")


# ──────────────────────────────────────────────────────────
# 4. PROMOTIONS & CATALOGUES
# ──────────────────────────────────────────────────────────

@register(Promotion)
class PromotionTranslationOptions(TranslationOptions):
    fields = ("titre", "description")


@register(CatalogueNumerique)
class CatalogueNumeriqueTranslationOptions(TranslationOptions):
    fields = ("titre",)


# ──────────────────────────────────────────────────────────
# 5. BANNIÈRES & SLIDER HERO
# ──────────────────────────────────────────────────────────

@register(BanniereHero)
class BanniereHeroTranslationOptions(TranslationOptions):
    fields = ("titre", "sous_titre", "texte_bouton")


@register(BanniereSecondaire)
class BanniereSecondaireTranslationOptions(TranslationOptions):
    fields = ("titre",)


# ──────────────────────────────────────────────────────────
# 6. RECETTES
# ──────────────────────────────────────────────────────────

@register(Recette)
class RecetteTranslationOptions(TranslationOptions):
    fields = ("titre", "description", "ingredients", "etapes", "astuce")


# ──────────────────────────────────────────────────────────
# 7. ACTUALITÉS / BLOG
# ──────────────────────────────────────────────────────────

@register(TagArticle)
class TagArticleTranslationOptions(TranslationOptions):
    fields = ("nom",)


@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ("titre", "chapeau", "contenu")


# ──────────────────────────────────────────────────────────
# 8. PROGRAMME DE FIDÉLITÉ
# ──────────────────────────────────────────────────────────

@register(AvantagesFidelite)
class AvantagesFideliteTranslationOptions(TranslationOptions):
    fields = ("titre", "description")


# ──────────────────────────────────────────────────────────
# 9. ÉQUIPE & RH
# ──────────────────────────────────────────────────────────
# MembreEquipe.nom/prenom ne sont pas traduits (noms propres).
# OffreEmploi : departement/magasin restent identiques (FK, pas du texte).

@register(Departement)
class DepartementTranslationOptions(TranslationOptions):
    fields = ("nom", "description")


@register(MembreEquipe)
class MembreEquipeTranslationOptions(TranslationOptions):
    fields = ("poste", "citation")


@register(OffreEmploi)
class OffreEmploiTranslationOptions(TranslationOptions):
    fields = ("titre", "description", "profil_recherche", "avantages", "salaire_indicatif")


# ──────────────────────────────────────────────────────────
# 13. FAQ
# ──────────────────────────────────────────────────────────

@register(CategorieFAQ)
class CategorieFAQTranslationOptions(TranslationOptions):
    fields = ("nom",)


@register(QuestionFAQ)
class QuestionFAQTranslationOptions(TranslationOptions):
    fields = ("question", "reponse")


# ──────────────────────────────────────────────────────────
# 15. STATISTIQUES CLÉS
# ──────────────────────────────────────────────────────────

@register(ChiffreCle)
class ChiffreCleTranslationOptions(TranslationOptions):
    fields = ("libelle",)