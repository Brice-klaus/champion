"""
==============================================================
  LE CHAMPION SUPERMARCHÉ TOGO — urls.py (racine du projet)
==============================================================
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ── Titre & sous-titre de l'interface admin ──────────────────
admin.site.site_header  = "Le Champion Supermarché — Administration"
admin.site.site_title   = "Champion Admin"
admin.site.index_title  = "Tableau de bord"

urlpatterns = [

    # ── Admin Django ─────────────────────────────────────────
    path("admin/", admin.site.urls),

    # ── Application principale ───────────────────────────────
    path("", include("supermarche.urls")),
]

# ── Handlers d'erreurs personnalisés ────────────────────────
handler404 = "supermarche.views.page_404"
handler500 = "supermarche.views.page_500"

# ── Servir les fichiers médias & statiques en développement ──
# En production ces fichiers sont servis par nginx / WhiteNoise
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )

    # django-debug-toolbar (optionnel — décommente si installé)
    # import debug_toolbar
    # urlpatterns = [
    #     path("__debug__/", include(debug_toolbar.urls)),
    # ] + urlpatterns