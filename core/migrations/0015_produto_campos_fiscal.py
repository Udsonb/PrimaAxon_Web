from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_produto_data_cotacao_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='taxa_cambio',
            field=models.DecimalField(decimal_places=4, default=1, max_digits=10, verbose_name='Taxa de Câmbio'),
        ),
        migrations.AddField(
            model_name='produto',
            name='desconto_mapeamento',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Desconto Mapeamento (%)'),
        ),
        migrations.AddField(
            model_name='produto',
            name='valor_com_desconto',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Valor c/ Desconto (R$)'),
        ),
        migrations.AddField(
            model_name='produto',
            name='ipi_reais',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='IPI (R$)'),
        ),
        migrations.AddField(
            model_name='produto',
            name='icms_reais',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='ICMS (R$)'),
        ),
        migrations.AddField(
            model_name='produto',
            name='difal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='DIFAL (%)'),
        ),
        migrations.AddField(
            model_name='produto',
            name='difal_reais',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='DIFAL (R$)'),
        ),
        migrations.AddField(
            model_name='produto',
            name='icms_compra',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='ICMS Compra (%)'),
        ),
        migrations.AlterField(
            model_name='produto',
            name='preco_fornecedor',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Preço Fornecedor'),
        ),
        migrations.AlterField(
            model_name='produto',
            name='unit_reais',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Custo Total (R$)'),
        ),
    ]
