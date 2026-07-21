"""
=============================================================
  LE CHAMPION SUPERMARCHÉ TOGO — Modèles Django
  Site Vitrine Moderne
=============================================================
"""

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.urls import  reverse

# ──────────────────────────────────────────────────────────
# 1. PARAMÈTRES GÉNÉRAUX DU SITE
# ──────────────────────────────────────────────────────────

class ParametresSite(models.Model):
    """Configuration globale du site vitrine."""

    nom_enseigne          = models.CharField(max_length=100, default="Le Champion Supermarché")
    slogan                = models.CharField(max_length=200, blank=True)
    description_courte    = models.TextField(blank=True, help_text="Résumé affiché dans le <meta description>")
    logo                  = models.ImageField(upload_to="site/logo/", blank=True)
    favicon               = models.ImageField(upload_to="site/favicon/", blank=True)
    couleur_primaire      = models.CharField(max_length=7, default="#D62828",
                                             help_text="Code hex ex: #D62828")
    couleur_secondaire    = models.CharField(max_length=7, default="#F7A72A")
    email_contact         = models.EmailField(blank=True)
    telephone_principal   = models.CharField(max_length=20, blank=True)
    facebook_url          = models.URLField(blank=True)
    instagram_url         = models.URLField(blank=True)
    whatsapp_numero       = models.CharField(max_length=20, blank=True)
    google_maps_embed     = models.TextField(blank=True, help_text="Code iframe Google Maps")
    mentions_legales      = models.TextField(blank=True)
    politique_confidentialite = models.TextField(blank=True)

    class Meta:
        verbose_name        = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"

    def __str__(self):
        return self.nom_enseigne

    def save(self, *args, **kwargs):
        # Singleton : un seul enregistrement autorisé
        self.pk = 1
        super().save(*args, **kwargs)


# ──────────────────────────────────────────────────────────
# 2. MAGASINS / POINTS DE VENTE
# ──────────────────────────────────────────────────────────

class Ville(models.Model):
    nom  = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Ville"
        ordering     = ["nom"]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Magasin(models.Model):
    """Un point de vente Le Champion."""

    nom            = models.CharField(max_length=150)
    slug           = models.SlugField(unique=True, blank=True)
    ville          = models.ForeignKey(Ville, on_delete=models.PROTECT, related_name="magasins")
    adresse        = models.TextField()
    telephone      = models.CharField(max_length=20, blank=True)
    email          = models.EmailField(blank=True)
    latitude       = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude      = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    photo          = models.ImageField(upload_to="magasins/photos/", blank=True)
    horaires       = models.TextField(blank=True, help_text="Ex: Lun-Sam 8h-21h / Dim 9h-18h")
    est_ouvert_24h = models.BooleanField(default=False)
    est_actif      = models.BooleanField(default=True)
    ordre          = models.PositiveSmallIntegerField(default=0, help_text="Ordre d'affichage")
    date_ouverture = models.DateField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Magasin"
        ordering     = ["ordre", "nom"]

    def __str__(self):
        return f"{self.nom} — {self.ville}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.nom}-{self.ville}")
        super().save(*args, **kwargs)


class ServiceMagasin(models.Model):
    """Services disponibles dans un magasin (parking, boulangerie, pharmacie…)."""

    ICONE_CHOICES = [
        ("parking",      "🅿️  Parking"),
        ("boulangerie",  "🥖 Boulangerie"),
        ("pharmacie",    "💊 Pharmacie / Parapharmacie"),
        ("wifi",         "📶 Wi-Fi gratuit"),
        ("livraison",    "🚚 Livraison à domicile"),
        ("drive",        "🚗 Drive"),
        ("retrait",      "📦 Point relais / Retrait"),
        ("restaurant",   "🍽️  Restauration"),
        ("banque",       "🏦 Service bancaire"),
        ("autre",        "✅ Autre"),
    ]

    magasin = models.ForeignKey(Magasin, on_delete=models.CASCADE, related_name="services")
    type    = models.CharField(max_length=20, choices=ICONE_CHOICES)
    libelle = models.CharField(max_length=100, blank=True, help_text="Surcharge du libellé par défaut")

    class Meta:
        verbose_name        = "Service du magasin"
        verbose_name_plural = "Services du magasin"
        unique_together     = ("magasin", "type")

    def __str__(self):
        return f"{self.magasin} — {self.get_type_display()}"


# ──────────────────────────────────────────────────────────
# 3. CATALOGUE PRODUITS
# ──────────────────────────────────────────────────────────

class RayonCategorie(models.Model):
    """Grande famille de rayons (Épicerie, Hygiène, Frais, etc.)."""

    nom        = models.CharField(max_length=100)
    slug       = models.SlugField(unique=True, blank=True)
    icone      = models.CharField(max_length=10, blank=True, help_text="Emoji ou classe d'icône")
    description = models.TextField(blank=True)
    image      = models.ImageField(upload_to="rayons/", blank=True)
    ordre      = models.PositiveSmallIntegerField(default=0)
    est_visible = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Catégorie de rayon"
        verbose_name_plural = "Catégories de rayons"
        ordering            = ["ordre", "nom"]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class SousCategorie(models.Model):
    """Sous-rayon (ex : Laits infantiles dans Bébé)."""

    categorie  = models.ForeignKey(RayonCategorie, on_delete=models.CASCADE, related_name="sous_categories")
    nom        = models.CharField(max_length=100)
    slug       = models.SlugField(blank=True)
    ordre      = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = "Sous-catégorie"
        verbose_name_plural = "Sous-catégories"
        ordering            = ["ordre", "nom"]
        unique_together     = ("categorie", "slug")

    def __str__(self):
        return f"{self.categorie} > {self.nom}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Marque(models.Model):
    nom        = models.CharField(max_length=100)
    slug       = models.SlugField(unique=True, blank=True)
    logo       = models.ImageField(upload_to="marques/logos/", blank=True)
    est_locale = models.BooleanField(default=False, help_text="Marque togolaise / locale")

    class Meta:
        verbose_name = "Marque"
        ordering     = ["nom"]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Produit(models.Model):
    """Produit référencé dans le catalogue vitrine."""

    UNITE_CHOICES = [
        ("piece",  "Pièce"),
        ("kg",     "Kilogramme"),
        ("g",      "Gramme"),
        ("l",      "Litre"),
        ("cl",     "Centilitre"),
        ("ml",     "Millilitre"),
        ("lot",    "Lot"),
        ("sachet", "Sachet"),
        ("boite",  "Boîte"),
        ("carton", "Carton"),
    ]

    # Identification
    nom           = models.CharField(max_length=200)
    slug          = models.SlugField(unique=True, blank=True)
    reference     = models.CharField(max_length=50, unique=True, blank=True)
    code_barre    = models.CharField(max_length=30, blank=True)

    # Classification
    sous_categorie = models.ForeignKey(SousCategorie, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name="produits")
    marque         = models.ForeignKey(Marque, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name="produits")

    # Description
    description      = models.TextField(blank=True)
    composition      = models.TextField(blank=True, help_text="Ingrédients / composition")
    contenance       = models.CharField(max_length=50, blank=True, help_text="Ex: 500 g, 1 L")
    unite_de_vente   = models.CharField(max_length=10, choices=UNITE_CHOICES, default="piece")
    conditionnement  = models.CharField(max_length=100, blank=True)

    # Prix (en FCFA)
    prix_public      = models.PositiveIntegerField(default=0, help_text="Prix en FCFA")
    prix_promo       = models.PositiveIntegerField(null=True, blank=True)
    est_en_promo     = models.BooleanField(default=False)

    # Média
    image_principale = models.ImageField(upload_to="produits/images/", blank=True)

    # Flags
    est_nouveau      = models.BooleanField(default=False)
    est_coup_de_coeur = models.BooleanField(default=False)
    est_local        = models.BooleanField(default=False, help_text="Produit made in Togo")
    est_bio          = models.BooleanField(default=False)
    est_visible      = models.BooleanField(default=True)
    est_disponible   = models.BooleanField(default=True)

    ordre            = models.PositiveSmallIntegerField(default=0)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        ordering     = ["ordre", "nom"]
        indexes      = [
            models.Index(fields=["slug"]),
            models.Index(fields=["est_visible", "est_disponible"]),
        ]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    @property
    def pourcentage_reduction(self):
        if self.est_en_promo and self.prix_promo and self.prix_public > 0:
            return round((1 - self.prix_promo / self.prix_public) * 100)
        return 0

    @property
    def prix_affiche(self):
        return self.prix_promo if self.est_en_promo and self.prix_promo else self.prix_public


class ImageProduit(models.Model):
    """Galerie photo d'un produit (vues multiples)."""

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="images_galerie")
    image   = models.ImageField(upload_to="produits/galerie/")
    alt     = models.CharField(max_length=150, blank=True)
    ordre   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Image produit"
        ordering     = ["ordre"]

    def __str__(self):
        return f"Image {self.ordre} — {self.produit}"

    
    def get_absolute_url(self):
        return reverse("supermarche:produit_detail", kwargs={"slug": self.slug})

# ──────────────────────────────────────────────────────────
# 4. PROMOTIONS & CATALOGUES
# ──────────────────────────────────────────────────────────

class Promotion(models.Model):
    """Opération promotionnelle (soldes, fêtes, événements)."""

    STATUT_CHOICES = [
        ("planifiee",  "Planifiée"),
        ("en_cours",   "En cours"),
        ("terminee",   "Terminée"),
        ("annulee",    "Annulée"),
    ]

    titre          = models.CharField(max_length=200)
    slug           = models.SlugField(unique=True, blank=True)
    description    = models.TextField(blank=True)
    image_banniere = models.ImageField(upload_to="promotions/bannieres/", blank=True)
    date_debut     = models.DateField()
    date_fin       = models.DateField()
    statut         = models.CharField(max_length=15, choices=STATUT_CHOICES, default="planifiee")
    est_mis_en_avant = models.BooleanField(default=False)
    produits       = models.ManyToManyField(Produit, blank=True, related_name="promotions")
    magasins       = models.ManyToManyField(Magasin, blank=True, related_name="promotions",
                                            help_text="Laisser vide = tous les magasins")
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Promotion"
        ordering     = ["-date_debut"]

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)


class CatalogueNumerique(models.Model):
    """Catalogue PDF téléchargeable (promotions, recettes, etc.)."""

    titre      = models.CharField(max_length=200)
    fichier    = models.FileField(upload_to="catalogues/")
    couverture = models.ImageField(upload_to="catalogues/couvertures/", blank=True)
    mois       = models.DateField(help_text="Mois de validité du catalogue")
    est_actif  = models.BooleanField(default=True)
    nb_pages   = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Catalogue numérique"
        verbose_name_plural = "Catalogues numériques"
        ordering            = ["-mois"]

    def __str__(self):
        return f"{self.titre} ({self.mois:%B %Y})"
    

# À ajouter dans supermarhe/models.py, à la suite de CatalogueNumerique


class CataloguePage(models.Model):
    """Une page individuelle d'un catalogue, pré-rendue en image."""

    catalogue = models.ForeignKey(
        CatalogueNumerique,
        on_delete=models.CASCADE,
        related_name="pages",
    )
    numero = models.PositiveSmallIntegerField(help_text="Numéro de la page (1, 2, 3...)")
    image  = models.ImageField(upload_to="catalogues/pages/")

    class Meta:
        verbose_name        = "Page de catalogue"
        verbose_name_plural = "Pages de catalogue"
        ordering            = ["numero"]
        unique_together     = ["catalogue", "numero"]

    def __str__(self):
        return f"{self.catalogue.titre} — page {self.numero}"


# ──────────────────────────────────────────────────────────
# 5. BANNIÈRES & SLIDER HERO
# ──────────────────────────────────────────────────────────

class BanniereHero(models.Model):
    """Slide du carousel principal de la page d'accueil."""

    titre          = models.CharField(max_length=150)
    sous_titre     = models.CharField(max_length=200, blank=True)
    image_desktop  = models.ImageField(upload_to="bannieres/desktop/")
    image_mobile   = models.ImageField(upload_to="bannieres/mobile/", blank=True)
    texte_bouton   = models.CharField(max_length=50, blank=True)
    lien_bouton    = models.CharField(max_length=300, blank=True)
    couleur_texte  = models.CharField(max_length=7, default="#FFFFFF")
    ordre          = models.PositiveSmallIntegerField(default=0)
    est_actif      = models.BooleanField(default=True)
    date_debut     = models.DateField(null=True, blank=True)
    date_fin       = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name        = "Bannière hero"
        verbose_name_plural = "Bannières hero"
        ordering            = ["ordre"]

    def __str__(self):
        return self.titre


class BanniereSecondaire(models.Model):
    """Bannières promotionnelles secondaires (mid-page, sidebar)."""

    POSITION_CHOICES = [
        ("accueil_milieu",   "Accueil — milieu de page"),
        ("accueil_bas",      "Accueil — bas de page"),
        ("catalogue_sidebar","Catalogue — barre latérale"),
        ("popup",            "Popup d'entrée"),
    ]

    titre     = models.CharField(max_length=150)
    image     = models.ImageField(upload_to="bannieres/secondaires/")
    lien      = models.CharField(max_length=300, blank=True)
    position  = models.CharField(max_length=25, choices=POSITION_CHOICES)
    ordre     = models.PositiveSmallIntegerField(default=0)
    est_actif = models.BooleanField(default=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin   = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name        = "Bannière secondaire"
        verbose_name_plural = "Bannières secondaires"
        ordering            = ["position", "ordre"]

    def __str__(self):
        return f"{self.titre} [{self.get_position_display()}]"


# ──────────────────────────────────────────────────────────
# 6. RECETTES
# ──────────────────────────────────────────────────────────

class Recette(models.Model):
    """Recette de cuisine mettant en valeur des produits du supermarché."""

    DIFFICULTE_CHOICES = [
        (1, "Facile"),
        (2, "Moyen"),
        (3, "Difficile"),
    ]

    titre             = models.CharField(max_length=200)
    slug              = models.SlugField(unique=True, blank=True)
    description       = models.TextField(blank=True)
    image             = models.ImageField(upload_to="recettes/images/")
    video_url         = models.URLField(blank=True, help_text="Lien YouTube / Vimeo")
    temps_preparation = models.PositiveSmallIntegerField(help_text="En minutes")
    temps_cuisson     = models.PositiveSmallIntegerField(default=0, help_text="En minutes")
    nombre_personnes  = models.PositiveSmallIntegerField(default=4)
    difficulte        = models.PositiveSmallIntegerField(choices=DIFFICULTE_CHOICES, default=1)
    ingredients       = models.TextField(help_text="Un ingrédient par ligne")
    etapes            = models.TextField(help_text="Une étape par ligne ou HTML")
    astuce            = models.TextField(blank=True)
    produits_lies     = models.ManyToManyField(Produit, blank=True, related_name="recettes")
    est_mise_en_avant = models.BooleanField(default=False)
    est_publiee       = models.BooleanField(default=True)
    auteur            = models.ForeignKey(User, on_delete=models.SET_NULL,
                                          null=True, blank=True, related_name="recettes")
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recette"
        ordering     = ["-created_at"]

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    @property
    def temps_total(self):
        return self.temps_preparation + self.temps_cuisson


# ──────────────────────────────────────────────────────────
# 7. ACTUALITÉS / BLOG
# ──────────────────────────────────────────────────────────

class TagArticle(models.Model):
    nom  = models.CharField(max_length=60)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name = "Tag article"

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Article(models.Model):
    """Actualité, communiqué de presse ou article du blog."""

    TYPE_CHOICES = [
        ("actualite",   "Actualité"),
        ("communique",  "Communiqué de presse"),
        ("blog",        "Article de blog"),
        ("evenement",   "Événement"),
    ]

    titre      = models.CharField(max_length=250)
    slug       = models.SlugField(unique=True, blank=True)
    type       = models.CharField(max_length=15, choices=TYPE_CHOICES, default="actualite")
    chapeau    = models.TextField(blank=True, help_text="Résumé court affiché en liste")
    contenu    = models.TextField()
    image      = models.ImageField(upload_to="articles/images/", blank=True)
    tags       = models.ManyToManyField(TagArticle, blank=True, related_name="articles")
    auteur     = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name="articles")
    est_publie     = models.BooleanField(default=False)
    est_mis_en_avant = models.BooleanField(default=False)
    date_publication = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Article"
        ordering     = ["-date_publication", "-created_at"]

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)


# ──────────────────────────────────────────────────────────
# 8. PROGRAMME DE FIDÉLITÉ
# ──────────────────────────────────────────────────────────

class CarteFidelite(models.Model):
    """Carte de fidélité « Champion Club »."""

    NIVEAU_CHOICES = [
        ("standard",  "Standard"),
        ("silver",    "Silver"),
        ("gold",      "Gold"),
        ("platinum",  "Platinum"),
    ]

    numero_carte    = models.CharField(max_length=20, unique=True)
    niveau          = models.CharField(max_length=10, choices=NIVEAU_CHOICES, default="standard")
    points_cumules  = models.PositiveIntegerField(default=0)
    points_disponibles = models.PositiveIntegerField(default=0)
    date_expiration = models.DateField(null=True, blank=True)
    est_active      = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Carte de fidélité"
        verbose_name_plural = "Cartes de fidélité"

    def __str__(self):
        return f"Carte {self.numero_carte} ({self.get_niveau_display()})"


class AvantagesFidelite(models.Model):
    """Avantages offerts par niveau de fidélité."""

    niveau      = models.CharField(max_length=10, choices=CarteFidelite.NIVEAU_CHOICES)
    titre       = models.CharField(max_length=100)
    description = models.TextField()
    icone       = models.CharField(max_length=10, blank=True)
    ordre       = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Avantage fidélité"
        ordering     = ["niveau", "ordre"]

    def __str__(self):
        return f"{self.get_niveau_display()} — {self.titre}"

    def get_niveau_display(self):
        return dict(CarteFidelite.NIVEAU_CHOICES).get(self.niveau, self.niveau)


# ──────────────────────────────────────────────────────────
# 9. ÉQUIPE & RH (vitrine recrutement)
# ──────────────────────────────────────────────────────────

class Departement(models.Model):
    nom         = models.CharField(max_length=100)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Département"

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class MembreEquipe(models.Model):
    """Portrait d'un collaborateur mis en avant sur le site."""

    nom        = models.CharField(max_length=100)
    prenom     = models.CharField(max_length=100)
    poste      = models.CharField(max_length=150)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name="membres")
    magasin    = models.ForeignKey(Magasin, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name="equipe")
    photo      = models.ImageField(upload_to="equipe/photos/", blank=True)
    citation   = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    ordre      = models.PositiveSmallIntegerField(default=0)
    est_visible = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Membre de l'équipe"
        ordering     = ["ordre", "nom"]

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.poste}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class OffreEmploi(models.Model):
    """Offre de recrutement publiée sur la page Carrières."""

    TYPE_CONTRAT_CHOICES = [
        ("cdi",       "CDI"),
        ("cdd",       "CDD"),
        ("stage",     "Stage"),
        ("alternance","Alternance"),
        ("freelance", "Freelance"),
    ]

    STATUT_CHOICES = [
        ("ouverte",   "Ouverte"),
        ("pourvue",   "Pourvue"),
        ("suspendue", "Suspendue"),
    ]

    titre          = models.CharField(max_length=200)
    slug           = models.SlugField(unique=True, blank=True)
    departement    = models.ForeignKey(Departement, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name="offres")
    magasin        = models.ForeignKey(Magasin, on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name="offres")
    type_contrat   = models.CharField(max_length=15, choices=TYPE_CONTRAT_CHOICES)
    description    = models.TextField()
    profil_recherche = models.TextField()
    avantages      = models.TextField(blank=True)
    salaire_indicatif = models.CharField(max_length=100, blank=True,
                                          help_text="Ex: 150 000 – 200 000 FCFA")
    statut         = models.CharField(max_length=12, choices=STATUT_CHOICES, default="ouverte")
    date_limite    = models.DateField(null=True, blank=True)
    date_publication = models.DateField(auto_now_add=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"
        ordering            = ["-date_publication"]

    def __str__(self):
        return f"{self.titre} ({self.get_type_contrat_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)


class CandidatureEmploi(models.Model):
    """Formulaire de candidature spontanée ou à une offre."""

    offre      = models.ForeignKey(OffreEmploi, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name="candidatures")
    prenom     = models.CharField(max_length=100)
    nom        = models.CharField(max_length=100)
    email      = models.EmailField()
    telephone  = models.CharField(max_length=20)
    cv         = models.FileField(upload_to="candidatures/cv/")
    lettre     = models.FileField(upload_to="candidatures/lettres/", blank=True)
    message    = models.TextField(blank=True)
    est_traitee = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Candidature"
        verbose_name_plural = "Candidatures"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.offre or 'Spontanée'}"


# ──────────────────────────────────────────────────────────
# 10. AVIS CLIENTS & TÉMOIGNAGES
# ──────────────────────────────────────────────────────────

class AvisClient(models.Model):
    """Avis laissé par un client, affiché en témoignage sur le site."""

    magasin    = models.ForeignKey(Magasin, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name="avis")
    prenom     = models.CharField(max_length=100)
    ville      = models.CharField(max_length=100, blank=True)
    note       = models.PositiveSmallIntegerField(
                    validators=[MinValueValidator(1), MaxValueValidator(5)])
    commentaire = models.TextField()
    est_modere  = models.BooleanField(default=False, help_text="Cocher pour afficher sur le site")
    est_mis_en_avant = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Avis client"
        verbose_name_plural = "Avis clients"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.prenom} ({'★' * self.note})"


# ──────────────────────────────────────────────────────────
# 11. CONTACT & MESSAGES
# ──────────────────────────────────────────────────────────

class MessageContact(models.Model):
    """Message envoyé via le formulaire de contact."""

    SUJET_CHOICES = [
        ("info",        "Demande d'information"),
        ("reclamation", "Réclamation"),
        ("partenariat", "Proposition de partenariat"),
        ("emploi",      "Emploi"),
        ("presse",      "Presse / Médias"),
        ("autre",       "Autre"),
    ]

    prenom     = models.CharField(max_length=100)
    nom        = models.CharField(max_length=100)
    email      = models.EmailField()
    telephone  = models.CharField(max_length=20, blank=True)
    sujet      = models.CharField(max_length=15, choices=SUJET_CHOICES, default="info")
    magasin    = models.ForeignKey(Magasin, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name="messages_contact")
    message    = models.TextField()
    est_lu     = models.BooleanField(default=False)
    est_traite = models.BooleanField(default=False)
    reponse    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.get_sujet_display()}"


# ──────────────────────────────────────────────────────────
# 12. NEWSLETTER
# ──────────────────────────────────────────────────────────

class AbonneNewsletter(models.Model):
    """Abonné à la newsletter du Champion."""

    LANGUE_CHOICES = [
        ("fr", "Français"),
        ("en", "Anglais"),
    ]

    email      = models.EmailField(unique=True)
    prenom     = models.CharField(max_length=100, blank=True)
    langue     = models.CharField(max_length=2, choices=LANGUE_CHOICES, default="fr")
    est_actif  = models.BooleanField(default=True)
    token_desinscription = models.CharField(max_length=64, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Abonné newsletter"
        verbose_name_plural = "Abonnés newsletter"
        ordering            = ["-created_at"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.token_desinscription:
            import secrets
            self.token_desinscription = secrets.token_hex(32)
        super().save(*args, **kwargs)


# ──────────────────────────────────────────────────────────
# 13. FAQ
# ──────────────────────────────────────────────────────────

class CategorieFAQ(models.Model):
    nom   = models.CharField(max_length=100)
    slug  = models.SlugField(unique=True, blank=True)
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = "Catégorie FAQ"
        verbose_name_plural = "Catégories FAQ"
        ordering            = ["ordre"]

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class QuestionFAQ(models.Model):
    """Question / réponse affichée dans la FAQ."""

    categorie  = models.ForeignKey(CategorieFAQ, on_delete=models.CASCADE, related_name="questions")
    question   = models.CharField(max_length=300)
    reponse    = models.TextField()
    ordre      = models.PositiveSmallIntegerField(default=0)
    est_publie = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Question FAQ"
        ordering     = ["categorie__ordre", "ordre"]

    def __str__(self):
        return self.question


# ──────────────────────────────────────────────────────────
# 14. PARTENAIRES & FOURNISSEURS
# ──────────────────────────────────────────────────────────

class Partenaire(models.Model):
    """Marque ou fournisseur partenaire affiché sur le site."""

    TYPE_CHOICES = [
        ("fournisseur",  "Fournisseur"),
        ("institutionnel","Partenaire institutionnel"),
        ("media",        "Partenaire média"),
    ]

    nom       = models.CharField(max_length=150)
    logo      = models.ImageField(upload_to="partenaires/logos/")
    site_web  = models.URLField(blank=True)
    type      = models.CharField(max_length=20, choices=TYPE_CHOICES, default="fournisseur")
    ordre     = models.PositiveSmallIntegerField(default=0)
    est_actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Partenaire"
        ordering     = ["ordre", "nom"]

    def __str__(self):
        return self.nom


# ──────────────────────────────────────────────────────────
# 15. STATISTIQUES CLÉS (chiffres mis en avant)
# ──────────────────────────────────────────────────────────

class ChiffreCle(models.Model):
    """Indicateur mis en avant sur la page À propos."""

    libelle   = models.CharField(max_length=100, help_text="Ex: Magasins au Togo")
    valeur    = models.CharField(max_length=20,  help_text="Ex: 12, +50 000, 30 ans")
    icone     = models.CharField(max_length=10, blank=True, help_text="Emoji ou classe")
    ordre     = models.PositiveSmallIntegerField(default=0)
    est_actif = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Chiffre clé"
        verbose_name_plural = "Chiffres clés"
        ordering            = ["ordre"]

    def __str__(self):
        return f"{self.valeur} {self.libelle}"
    
    
    

import uuid
from urllib.parse import quote

from django.conf import settings
from django.db import models
from django.urls import reverse


class Reservation(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente de confirmation"),
        ("confirmee", "Confirmée"),
        ("prete", "Prête (retrait)"),
        ("en_livraison", "En cours de livraison"),
        ("recuperee", "Récupérée / Livrée"),
        ("annulee", "Annulée"),
    ]
    TYPE_RECUP_CHOICES = [
        ("retrait", "Retrait en magasin"),
        ("livraison", "Livraison à domicile"),
    ]

    numero = models.CharField(max_length=12, unique=True, editable=False)

    client_nom       = models.CharField("Nom complet", max_length=120)
    client_telephone = models.CharField("Téléphone", max_length=20)
    client_email     = models.EmailField("Email", blank=True)

    type_recuperation = models.CharField(max_length=12, choices=TYPE_RECUP_CHOICES, default="retrait")
    magasin           = models.ForeignKey("Magasin", on_delete=models.PROTECT, null=True, blank=True, related_name="reservations")
    adresse_livraison = models.TextField("Adresse de livraison", blank=True)
    creneau_souhaite  = models.DateTimeField("Créneau souhaité")

    statut      = models.CharField(max_length=15, choices=STATUT_CHOICES, default="en_attente")
    note_client = models.TextField("Instructions particulières", blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    maj_le  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-cree_le"]
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"

    def __str__(self):
        return f"{self.numero} — {self.client_nom}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = f"RES-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("supermarche:reservation_confirmation", kwargs={"numero": self.numero})

    @property
    def total_estime(self):
        return sum(l.sous_total for l in self.lignes.all())

    def get_whatsapp_url(self):
        numero_pro = getattr(settings, "MAGASIN_WHATSAPP", "22893040702")
        message = (
            f"Bonjour, je vous contacte au sujet de ma réservation {self.numero} "
            f"({self.client_nom})."
        )
        return f"https://wa.me/{numero_pro}?text={quote(message)}"


class LigneReservation(models.Model):
    reservation = models.ForeignKey(Reservation, related_name="lignes", on_delete=models.CASCADE)
    produit     = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite    = models.PositiveIntegerField(default=1)
    prix_unitaire_capture = models.DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        verbose_name = "Ligne de réservation"
        verbose_name_plural = "Lignes de réservation"

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire_capture

    def __str__(self):
        return f"{self.quantite} × {self.produit.nom}"