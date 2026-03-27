"""
Faz upload dos arquivos de media locais (logos, fotos) para o GCS,
mas SOMENTE se o arquivo ainda não existir no bucket.
Usado no startup do Cloud Run quando USE_GCS=True.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Sobe arquivos de media local para o Google Cloud Storage'

    def handle(self, *args, **options):
        if not getattr(settings, 'USE_GCS', False):
            self.stdout.write('USE_GCS desativado — upload ignorado.')
            return

        try:
            from google.cloud import storage as gcs
        except ImportError:
            self.stdout.write(self.style.ERROR('google-cloud-storage não instalado.'))
            return

        bucket_name = settings.GS_BUCKET_NAME
        media_root = os.path.join(settings.BASE_DIR, 'media')

        if not os.path.exists(media_root):
            self.stdout.write('Pasta media/ não encontrada — upload ignorado.')
            return

        client = gcs.Client()
        bucket = client.bucket(bucket_name)
        uploaded = 0
        skipped = 0

        for dirpath, _, filenames in os.walk(media_root):
            for filename in filenames:
                local_path = os.path.join(dirpath, filename)
                relative = os.path.relpath(local_path, media_root).replace('\\', '/')
                blob_name = f'media/{relative}'
                blob = bucket.blob(blob_name)

                if blob.exists():
                    skipped += 1
                    continue

                blob.upload_from_filename(local_path)
                uploaded += 1
                self.stdout.write(f'  Upload: {blob_name}')

        self.stdout.write(self.style.SUCCESS(
            f'Upload concluído: {uploaded} enviados, {skipped} já existiam.'
        ))
