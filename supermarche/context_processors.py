from .panier import Panier


def panier_context(request):
    """
    Rend `panier_count` disponible dans tous les templates,
    notamment pour le badge du panier dans le header.
    """
    return {
        "panier_count": len(Panier(request)),
    }
    
def nav_active_context(request):
    """
    Calcule quel groupe de menu (Rayons / Produits / Promotions) est actif,
    pour l'affichage de l'état "en cours" dans la nav desktop et mobile.
    """
    view_name = request.resolver_match.view_name if request.resolver_match else None

    return {
        "nav_view_name": view_name,
        "nav_rayons_actif": view_name == "supermarche:rayoncategorie_detail",
        "nav_produits_actif": view_name in [
            "supermarche:produits_tous",
            "supermarche:produits_nouveautes",
            "supermarche:produits_coups_de_coeur",
            "supermarche:produits_locaux",
        ],
        "nav_promos_actif": view_name in [
            "supermarche:promotions_liste",
            "supermarche:promotion_detail",
            "supermarche:produits_promo",
        ],
    }