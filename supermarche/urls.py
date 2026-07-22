# supermarhe/urls.py — à fusionner avec l'existant

from django.urls import path
from . import views

app_name = "supermarche"

urlpatterns = [
    path("", views.AccueilView.as_view(), name="accueil"),

    # ---------- Catalogue produits ----------
    path("raiyoncategorie/", views.RayonCategorieView.as_view(), name="raiyoncategorie"),
    path("catalogue/<slug:slug>/", views.CategorieProduitView.as_view(), name="categorie_produits"),
    #path("catalogue/<slug:cat_slug>/<slug:sc_slug>/", views.SousCategorieProduitView.as_view(), name="sous_categorie_produits"),
    path("produit/<slug:slug>/", views.ProduitDetailView.as_view(), name="produit_detail"),
    

    # ---------- Listes transverses de produits ----------
    path("nouveautes/", views.ProduitsNouveautesView.as_view(), name="produits_nouveautes"),
    path("produits-locaux/", views.ProduitsLocauxView.as_view(), name="produits_locaux"),
    path("promotions/produits/", views.ProduitsPromoView.as_view(), name="produits_promo"),

    # ---------- Promotions & catalogues numériques ----------
    path("promotions/", views.PromotionsListView.as_view(), name="promotions_liste"),
    path("promotion_detail/<slug:slug>/", views.PromotionDetailView.as_view(), name="promotion_detail"),
    path("catalogues/", views.CataloguesNumeriquesView.as_view(), name="catalogues_liste"),
    path("catalogues/<int:pk>/", views.CatalogueDetailView.as_view(), name="catalogue_detail"),

    # ---------- Recettes ----------
    path("recettes/", views.RecetteListView.as_view(), name="recette_liste"),
    path("recettes/<slug:slug>/", views.RecetteDetailView.as_view(), name="recette_detail"),

    # ---------- Blog ----------
    path("actualites/", views.ArticleListView.as_view(), name="article_liste"),
    path("actualites/<slug:slug>/", views.ArticleDetailView.as_view(), name="article_detail"),

    # ---------- Magasins ----------
    path("magasin_liste/", views.MagasinListView.as_view(), name="magasin_liste"),
    path("magasin_detail/<slug:slug>/", views.MagasinDetailView.as_view(), name="magasin_detail"),

    # ---------- Fidélité ----------
    path("fidelite/", views.FideliteView.as_view(), name="fidelite"),

    # ---------- À propos / Carrières / Contact ----------
    path("a-propos/", views.AProposView.as_view(), name="a_propos"),
    path("carrieres/", views.CarrieresView.as_view(), name="carrieres_liste"),
    path("carrieres/<slug:slug>/", views.OffreEmploiDetailView.as_view(), name="offre_detail"),
    path("contact/", views.ContactView.as_view(), name="contact"),

    # ---------- Recherche ----------
    path("recherche/", views.RechercheView.as_view(), name="recherche"),
    path("rayoncategorie_detail/<slug:slug>/", views.RayonCategorieDetailView.as_view(), name="rayoncategorie_detail"),
    
    path("produits/coups-de-coeur/", views.ProduitsCoupsDeCoeurView.as_view(), name="produits_coups_de_coeur"),
    path("produits/tous/", views.ProduitsTousView.as_view(), name="produits_tous"),
    
    
    
    path("panier/", views.PanierView.as_view(), name="panier"),
    path("panier/modifier/<int:produit_id>/", views.PanierModifierView.as_view(), name="panier_modifier"),
    path("panier/ajouter/<int:produit_id>/", views.PanierAjouterView.as_view(), name="panier_ajouter"),
    path("panier/retirer/<int:produit_id>/", views.PanierRetirerView.as_view(), name="panier_retirer"),
    path("reservation/", views.ReservationCreateView.as_view(), name="reservation_creer"),
    path("reservation/<str:numero>/", views.ReservationConfirmationView.as_view(), name="reservation_confirmation"),
        
]