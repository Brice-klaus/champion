# Le Champion Supermarché Togo — Schéma des modèles Django

## Vue d'ensemble des 15 modules

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     LE CHAMPION SUPERMARCHÉ TOGO                        │
│                       Modèles Django — Vitrine                          │
└─────────────────────────────────────────────────────────────────────────┘

╔══════════════════════╗   ╔══════════════════════╗   ╔═══════════════════╗
║  1. SITE             ║   ║  2. MAGASINS          ║   ║  3. CATALOGUE     ║
║─────────────────────║   ║─────────────────────║   ║──────────────────║
║  ParametresSite      ║   ║  Ville               ║   ║  RayonCategorie   ║
║  (singleton)         ║   ║  └─► Magasin         ║   ║  └─► SousCategorie║
║                      ║   ║      └─► ServiceMagasin   ║      └─► Produit  ║
╚══════════════════════╝   ╚══════════════════════╝   ║          ├ Marque  ║
                                                       ║          └ ImageProduit
╔══════════════════════╗   ╔══════════════════════╗   ╚═══════════════════╝
║  4. PROMOTIONS        ║   ║  5. BANNIÈRES        ║
║─────────────────────║   ║─────────────────────║
║  Promotion           ║   ║  BanniereHero        ║
║  └─►Produit (M2M)    ║   ║  BanniereSecondaire  ║
║  └─►Magasin (M2M)    ║   ╚══════════════════════╝
║  CatalogueNumerique  ║
╚══════════════════════╝

╔══════════════════════╗   ╔══════════════════════╗   ╔═══════════════════╗
║  6. RECETTES         ║   ║  7. ARTICLES / BLOG   ║   ║  8. FIDÉLITÉ      ║
║─────────────────────║   ║─────────────────────║   ║──────────────────║
║  Recette             ║   ║  TagArticle          ║   ║  CarteFidelite    ║
║  └─►Produit (M2M)    ║   ║  Article             ║   ║  AvantagesFidelite║
║                      ║   ║  └─►Tag (M2M)        ║   ╚═══════════════════╝
╚══════════════════════╝   ╚══════════════════════╝

╔══════════════════════╗   ╔══════════════════════╗   ╔═══════════════════╗
║  9. ÉQUIPE & RH      ║   ║  10. AVIS CLIENTS     ║   ║  11. CONTACT      ║
║─────────────────────║   ║─────────────────────║   ║──────────────────║
║  Departement         ║   ║  AvisClient          ║   ║  MessageContact   ║
║  MembreEquipe        ║   ║  └─►Magasin (FK)     ║   ║  └─►Magasin (FK)  ║
║  OffreEmploi         ║   ╚══════════════════════╝   ╚═══════════════════╝
║  CandidatureEmploi   ║
╚══════════════════════╝

╔══════════════════════╗   ╔══════════════════════╗   ╔═══════════════════╗
║  12. NEWSLETTER       ║   ║  13. FAQ              ║   ║  14. PARTENAIRES  ║
║─────────────────────║   ║─────────────────────║   ║──────────────────║
║  AbonneNewsletter    ║   ║  CategorieFAQ        ║   ║  Partenaire       ║
║                      ║   ║  └─► QuestionFAQ     ║   ╚═══════════════════╝
╚══════════════════════╝   ╚══════════════════════╝

╔══════════════════════╗
║  15. CHIFFRES CLÉS   ║
║─────────────────────║
║  ChiffreCle          ║
╚══════════════════════╝
```

## Récapitulatif des modèles (26 au total)

| # | Modèle | Module | Description |
|---|--------|--------|-------------|
| 1 | `ParametresSite` | Site | Configuration globale (singleton) |
| 2 | `Ville` | Magasins | Villes du Togo |
| 3 | `Magasin` | Magasins | Points de vente |
| 4 | `ServiceMagasin` | Magasins | Services par magasin |
| 5 | `RayonCategorie` | Catalogue | Grandes familles de rayons |
| 6 | `SousCategorie` | Catalogue | Sous-rayons |
| 7 | `Marque` | Catalogue | Marques produits |
| 8 | `Produit` | Catalogue | Produits du catalogue |
| 9 | `ImageProduit` | Catalogue | Photos galerie produit |
| 10 | `Promotion` | Promotions | Opérations promo |
| 11 | `CatalogueNumerique` | Promotions | Catalogues PDF |
| 12 | `BanniereHero` | Bannières | Slider page d'accueil |
| 13 | `BanniereSecondaire` | Bannières | Bannières internes |
| 14 | `Recette` | Recettes | Recettes de cuisine |
| 15 | `TagArticle` | Blog | Tags articles |
| 16 | `Article` | Blog | Actualités & blog |
| 17 | `CarteFidelite` | Fidélité | Cartes Champion Club |
| 18 | `AvantagesFidelite` | Fidélité | Avantages par niveau |
| 19 | `Departement` | RH | Départements internes |
| 20 | `MembreEquipe` | RH | Portraits collaborateurs |
| 21 | `OffreEmploi` | RH | Offres de recrutement |
| 22 | `CandidatureEmploi` | RH | Formulaires de candidature |
| 23 | `AvisClient` | Avis | Témoignages clients |
| 24 | `MessageContact` | Contact | Formulaire de contact |
| 25 | `AbonneNewsletter` | Newsletter | Abonnés email |
| 26 | `CategorieFAQ` | FAQ | Catégories FAQ |
| 27 | `QuestionFAQ` | FAQ | Questions/réponses |
| 28 | `Partenaire` | Partenaires | Logos partenaires |
| 29 | `ChiffreCle` | À propos | Indicateurs clés |

## Structure des fichiers

```
lechampion/
├── manage.py
├── requirements.txt
├── lechampion/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── supermarche/
    ├── __init__.py
    ├── apps.py
    ├── models.py        ← modèles complets
    ├── admin.py         ← interface admin
    ├── views.py         ← à créer
    ├── urls.py          ← à créer
    ├── serializers.py   ← si API REST
    └── migrations/
        └── 0001_initial.py
```

## Commandes de démarrage

```bash
# Installer les dépendances
pip install -r requirements.txt

# Créer les migrations
python manage.py makemigrations supermarche

# Appliquer les migrations
python manage.py migrate

# Créer un super-utilisateur admin
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver
```

## Champs notables

### Produit
- `prix_public` / `prix_promo` en **FCFA** (entiers)
- Propriété calculée `pourcentage_reduction`
- Propriété `prix_affiche` (retourne le bon prix auto)
- Flags : `est_local` (made in Togo), `est_bio`, `est_nouveau`, `est_coup_de_coeur`

### Magasin
- Coordonnées GPS pour intégration Google Maps
- `est_ouvert_24h` pour la pastille « 24h/24 »

### AbonneNewsletter
- `token_desinscription` généré automatiquement (lien de désinscription RGPD)

### ParametresSite
- Pattern **singleton** : `.save()` force `pk=1`