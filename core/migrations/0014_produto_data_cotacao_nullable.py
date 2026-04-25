from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_perfil_cargo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='data_ultima_cotacao',
            field=models.DateField(blank=True, null=True, verbose_name='Data da Última Cotação'),
        ),
    ]
