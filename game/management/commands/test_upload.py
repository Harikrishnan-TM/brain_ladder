import logging
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Test file upload to Supabase storage"

    def handle(self, *args, **options):
        try:
            # Create a small dummy file
            file_content = b"Hello Supabase!"
            file_name = "test/test_upload.txt"  # path inside bucket

            # Save using Django's default storage (S3Boto3Storage)
            file = default_storage.save(file_name, ContentFile(file_content))
            file_url = default_storage.url(file)

            self.stdout.write(self.style.SUCCESS(f"✅ File uploaded successfully! URL: {file_url}"))
        except Exception as e:
            logger.exception("❌ Upload failed")
            self.stdout.write(self.style.ERROR(f"❌ Upload failed: {e}"))
