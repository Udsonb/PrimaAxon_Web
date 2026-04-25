from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_itemmo_extras'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='cargo',
            field=models.CharField(
                choices=[
                    ('diretor_geral',      'Diretor Geral'),
                    ('diretor_setor',      'Diretor de Setor'),
                    ('gerente_pre_vendas', 'Gerente Pré-Vendas'),
                    ('supervisor',         'Supervisor'),
                    ('gerente_comercial',  'Gerente Comercial'),
                    ('executivo',          'Executivo'),
                    ('analista',           'Analista'),
                    ('gerente_compras',    'Gerente de Compras'),
                    ('comprador',          'Comprador'),
                    ('orcamentista',       'Orçamentista'),
                ],
                default='analista',
                max_length=30,
                verbose_name='Cargo',
            ),
        ),
    ]
