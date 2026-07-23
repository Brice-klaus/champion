"""
resources.py — Ressources d'import/export pour Le Champion Supermarché
"""
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import (
    Produit, SousCategorie, Marque,
    Magasin, Ville,
    Promotion, RayonCategorie,
    Article, Recette, OffreEmploi, Departement,
)


class ProduitResource(resources.ModelResource):
    """
    Ressource principale : import/export en masse du catalogue produits.
    Les colonnes sous_categorie / marque acceptent le NOM en clair dans le CSV,
    pas la clé primaire — plus pratique pour une saisie manuelle en Excel.
    """
    sous_categorie = fields.Field(
        column_name="sous_categorie",
        attribute="sous_categorie",
        widget=ForeignKeyWidget(SousCategorie, field="nom"),
    )
    marque = fields.Field(
        column_name="marque",
        attribute="marque",
        widget=ForeignKeyWidget(Marque, field="nom"),
    )

    class Meta:
        model = Produit
        import_id_fields = ["reference"]  # évite les doublons : ré-importer met à jour plutôt que dupliquer
        fields = (
            "id", "nom", "slug", "reference", "code_barre",
            "sous_categorie", "marque",
            "description", "composition", "contenance",
            "unite_de_vente", "conditionnement",
            "prix_public", "prix_promo", "est_en_promo",
            "est_nouveau", "est_coup_de_coeur", "est_local", "est_bio",
            "est_visible", "est_disponible", "ordre",
        )
        export_order = fields


class MagasinResource(resources.ModelResource):
    ville = fields.Field(
        column_name="ville",
        attribute="ville",
        widget=ForeignKeyWidget(Ville, field="nom"),
    )

    class Meta:
        model = Magasin
        import_id_fields = ["slug"]
        fields = (
            "id", "nom", "slug", "ville", "adresse",
            "telephone", "email", "latitude", "longitude",
            "horaires", "est_ouvert_24h", "est_actif", "ordre",
        )


class PromotionResource(resources.ModelResource):
    class Meta:
        model = Promotion
        import_id_fields = ["slug"]
        fields = (
            "id", "titre", "slug", "description",
            "date_debut", "date_fin", "statut", "est_mis_en_avant",
        )
        # produits / magasins (M2M) volontairement exclus :
        # l'import M2M via CSV est fragile, à gérer manuellement dans l'admin après import


class RayonCategorieResource(resources.ModelResource):
    class Meta:
        model = RayonCategorie
        import_id_fields = ["slug"]
        fields = ("id", "nom", "slug", "icone", "description", "ordre", "est_visible")


class ArticleResource(resources.ModelResource):
    class Meta:
        model = Article
        import_id_fields = ["slug"]
        fields = (
            "id", "titre", "slug", "type", "chapeau", "contenu",
            "est_publie", "est_mis_en_avant", "date_publication",
        )


class RecetteResource(resources.ModelResource):
    class Meta:
        model = Recette
        import_id_fields = ["slug"]
        fields = (
            "id", "titre", "slug", "description",
            "temps_preparation", "temps_cuisson", "nombre_personnes",
            "difficulte", "ingredients", "etapes", "astuce",
            "est_mise_en_avant", "est_publiee",
        )


class OffreEmploiResource(resources.ModelResource):
    departement = fields.Field(
        column_name="departement",
        attribute="departement",
        widget=ForeignKeyWidget(Departement, field="nom"),
    )

    class Meta:
        model = OffreEmploi
        import_id_fields = ["slug"]
        fields = (
            "id", "titre", "slug", "departement", "type_contrat",
            "description", "profil_recherche", "avantages",
            "salaire_indicatif", "statut", "date_limite",
        )