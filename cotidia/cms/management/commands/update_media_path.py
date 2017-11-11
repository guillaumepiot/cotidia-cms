from django.core.management.base import BaseCommand
from cotidia.cms.models import PageTranslation


class Command(BaseCommand):
    help = 'Replace the media path in pages content.'

    def add_arguments(self, parser):
        parser.add_argument('original_path', type=str)
        parser.add_argument('new_path', type=str)

    def handle(self, *args, **options):
        for page in PageTranslation.objects.all():

            regions = page.regions

            regions = regions.replace(options['original_path'], options['new_path'])

            page.regions = regions
            page.save()

            self.stdout.write(self.style.SUCCESS('Region updated "%s"' % page))
