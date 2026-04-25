from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_produto_campos_fiscal'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracaoFinanceira',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custos_adm', models.DecimalField(decimal_places=2, default=5, max_digits=5, verbose_name='Custos Adm (%)')),
                ('ll_minimo', models.DecimalField(decimal_places=2, default=15, max_digits=5, verbose_name='LL Mínimo Desejado (%)')),
                ('premiacao_normal', models.DecimalField(decimal_places=2, default='2.52', max_digits=5, verbose_name='Premiação Normal (%)')),
                ('premiacao_publicada', models.DecimalField(decimal_places=2, default='1.09', max_digits=5, verbose_name='Premiação Já Publicada (%)')),
                ('wacc_locacao', models.DecimalField(decimal_places=2, default=1, max_digits=5, verbose_name='WACC Locação (%/mês)')),
                ('payback_spare_parts', models.DecimalField(decimal_places=2, default=60, max_digits=5, verbose_name='Payback Spare Parts (% do Custo)')),
                ('dias_cotacao_grupo1', models.IntegerField(default=30, verbose_name='Validade Grupo 1 (dias)')),
                ('dias_cotacao_grupo2', models.IntegerField(default=60, verbose_name='Validade Grupo 2 (dias)')),
                ('dias_cotacao_grupo3', models.IntegerField(default=90, verbose_name='Validade Grupo 3 (dias)')),
                ('fmt_vencida_dias', models.IntegerField(default=0, verbose_name='Alerta Vencida (≤ dias)')),
                ('fmt_proxima_dias', models.IntegerField(default=5, verbose_name='Alerta Próxima (≤ dias)')),
                ('desconto_ev', models.DecimalField(decimal_places=2, default=5, max_digits=5, verbose_name='Desconto EV (%)')),
                ('desconto_gerente', models.DecimalField(decimal_places=2, default=2, max_digits=5, verbose_name='Desconto Gerente (%)')),
                ('desconto_diretor', models.DecimalField(decimal_places=2, default=3, max_digits=5, verbose_name='Desconto Diretor (%)')),
            ],
            options={
                'verbose_name': 'Configuração Financeira',
            },
        ),
    ]
