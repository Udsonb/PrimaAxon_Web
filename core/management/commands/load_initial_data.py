"""
Carrega os dados iniciais (fixture) no banco de produção,
mas SOMENTE se o banco estiver vazio (evita duplicar dados).
Usado no startup do Cloud Run.
"""
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from core.models import Produto


class Command(BaseCommand):
    help = 'Carrega initial_data.json se o banco estiver vazio'

    def handle(self, *args, **options):
        if Produto.objects.exists():
            self.stdout.write(self.style.WARNING(
                'Banco já tem dados — carga ignorada.'
            ))
            return

        fixture_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', 'fixtures', 'initial_data.json'
        )
        fixture_path = os.path.normpath(fixture_path)

        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR(
                f'Fixture não encontrada: {fixture_path}'
            ))
            return

        self.stdout.write('Carregando dados iniciais...')
        call_command('loaddata', fixture_path, verbosity=1)
        self.stdout.write(self.style.SUCCESS('Dados carregados com sucesso!'))
