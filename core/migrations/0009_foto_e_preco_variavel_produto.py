from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_aumenta_maxlength_produto'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='produtos/', verbose_name='Foto do Produto'),
        ),
        migrations.AddField(
            model_name='produto',
            name='preco_variavel',
            field=models.BooleanField(default=False, help_text='Marque se o preço deste item é definido pela Mão de Obra do projeto', verbose_name='Preço Variável (M.O)'),
        ),
    ]
