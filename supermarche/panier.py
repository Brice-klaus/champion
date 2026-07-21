SESSION_KEY = "panier"


class Panier:
    def __init__(self, request):
        self.session = request.session
        panier = self.session.get(SESSION_KEY)
        if panier is None:
            panier = self.session[SESSION_KEY] = {}
        self.panier = panier

    def ajouter(self, produit, quantite=1):
        pid = str(produit.pk)
        if pid in self.panier:
            self.panier[pid]["quantite"] += quantite
        else:
            self.panier[pid] = {"quantite": quantite}
        self.enregistrer()

    def modifier_quantite(self, produit_id, quantite):
        pid = str(produit_id)
        if pid in self.panier:
            if quantite <= 0:
                del self.panier[pid]
            else:
                self.panier[pid]["quantite"] = quantite
            self.enregistrer()

    def retirer(self, produit_id):
        pid = str(produit_id)
        if pid in self.panier:
            del self.panier[pid]
            self.enregistrer()

    def vider(self):
        self.session[SESSION_KEY] = {}
        self.enregistrer()

    def enregistrer(self):
        self.session.modified = True

    def __iter__(self):
        from .models import Produit
        ids = self.panier.keys()
        produits = Produit.objects.filter(pk__in=ids)
        produits_map = {str(p.pk): p for p in produits}
        for pid, data in self.panier.items():
            produit = produits_map.get(pid)
            if produit is None:
                continue
            yield {
                "produit": produit,
                "quantite": data["quantite"],
                "sous_total": produit.prix_affiche * data["quantite"],
            }

    def __len__(self):
        return sum(item["quantite"] for item in self.panier.values())

    @property
    def total(self):
        return sum(item["sous_total"] for item in self)