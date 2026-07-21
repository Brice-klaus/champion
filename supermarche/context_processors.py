from .panier import Panier


def panier_context(request):
    """
    Rend `panier_count` disponible dans tous les templates,
    notamment pour le badge du panier dans le header.
    """
    return {
        "panier_count": len(Panier(request)),
    }