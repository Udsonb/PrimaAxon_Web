from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_foto_e_preco_variavel_produto'),
    ]

    operations = [
        migrations.AddField(
            model_name='projeto',
            name='revisao',
            field=models.IntegerField(default=0, verbose_name='Revisão'),
        ),
    ]
