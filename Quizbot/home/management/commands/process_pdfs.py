from django.core.management.base import BaseCommand
from home.utils import process_all_pdfs  

class Command(BaseCommand):
    help = 'Process all new or modified PDFs in the data directory'

    def handle(self, *args, **kwargs):
        all_text = process_all_pdfs()
        self.stdout.write(self.style.SUCCESS('Processed PDFs successfully'))
