"""
Carrega os dados iniciais (fixture) no banco de produção,
mas SOMENTE se o banco estiver vazio (evita duplicar dados).

--priority  : carrega apenas Empresa e auth.User (rápido, síncrono no startup)
sem flag    : carrega tudo (Produto, Projeto, etc.) — usado em background
"""
import os
import json
from django.core.management.base import BaseCommand
from django.core.management import call_command
from core.models import Empresa, Produto


from django.conf import settings as _settings
FIXTURE_PATH = os.path.join(_settings.BASE_DIR, 'fixtures', 'initial_data.json')

PRIORITY_MODELS = {'auth.group', 'core.empresa', 'auth.user', 'core.perfil'}


class Command(BaseCommand):
    help = 'Carrega initial_data.json se o banco estiver vazio'

    def add_arguments(self, parser):
        parser.add_argument(
            '--priority', action='store_true',
            help='Carrega apenas Empresa, User e Perfil (rápido)'
        )

    def handle(self, *args, **options):
        if not os.path.exists(FIXTURE_PATH):
            self.stdout.write(self.style.ERROR(f'Fixture não encontrada: {FIXTURE_PATH}'))
            return

        if options['priority']:
            self._load_priority()
        else:
            self._load_full()

    def _load_priority(self):
        if Empresa.objects.exists():
            self.stdout.write('Empresas já existem — carga prioritária ignorada.')
            return

        self.stdout.write('Carregando empresas e usuários...')
        with open(FIXTURE_PATH, encoding='utf-8') as f:
            all_data = json.load(f)

        priority_data = [obj for obj in all_data if obj['model'] in PRIORITY_MODELS]

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                         delete=False, encoding='utf-8') as tmp:
            json.dump(priority_data, tmp, ensure_ascii=False)
            tmp_path = tmp.name

        try:
            call_command('loaddata', tmp_path, verbosity=1)
            self.stdout.write(self.style.SUCCESS(
                f'{len(priority_data)} registros prioritários carregados.'
            ))
        finally:
            os.unlink(tmp_path)

    def _load_full(self):
        if Produto.objects.exists():
            self.stdout.write('Produtos já existem — carga completa ignorada.')
            return

        self.stdout.write('Carregando todos os dados (produtos, projetos...)...')
        call_command('loaddata', FIXTURE_PATH, verbosity=1)
        self.stdout.write(self.style.SUCCESS('Carga completa concluída.'))
