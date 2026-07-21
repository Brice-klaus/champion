# Fichier : supermarhe/management/commands/generer_pages_catalogue.py
#
# Dépendance système requise : poppler-utils
#   sudo apt install poppler-utils
#
# Dépendance Python requise :
#   pip install pdf2image

import io
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from pdf2image import convert_from_path

from supermarhe.models import CatalogueNumerique, CataloguePage


class Command(BaseCommand):
    help = "Convertit le PDF d'un CatalogueNumerique en une série d'images de pages (CataloguePage)."

    def add_arguments(self, parser):
        parser.add_argument("catalogue_id", type=int)
        parser.add_argument(
            "--dpi", type=int, default=150,
            help="Résolution de rendu des pages (150 = bon compromis netteté/poids).",
        )

    def handle(self, *args, **options):
        try:
            catalogue = CatalogueNumerique.objects.get(pk=options["catalogue_id"])
        except CatalogueNumerique.DoesNotExist:
            raise CommandError(f"Catalogue {options['catalogue_id']} introuvable.")

        if not catalogue.fichier:
            raise CommandError("Ce catalogue n'a pas de fichier PDF.")

        self.stdout.write(f"Conversion de « {catalogue.titre} »...")

        # Supprime les anciennes pages avant régénération
        catalogue.pages.all().delete()

        images = convert_from_path(catalogue.fichier.path, dpi=options["dpi"])

        for i, image in enumerate(images, start=1):
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=85)
            page = CataloguePage(catalogue=catalogue, numero=i)
            page.image.save(f"{catalogue.pk}_page_{i:02d}.jpg", ContentFile(buffer.getvalue()), save=True)
            self.stdout.write(f"  page {i}/{len(images)} générée")

        catalogue.nb_pages = len(images)
        catalogue.save(update_fields=["nb_pages"])

        self.stdout.write(self.style.SUCCESS(f"{len(images)} pages générées pour « {catalogue.titre} »."))