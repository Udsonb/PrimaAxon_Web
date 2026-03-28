from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_itemmo'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemmo',
            name='especificacao',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Especificação'),
        ),
        migrations.AddField(
            model_name='itemmo',
            name='ativo',
            field=models.BooleanField(default=True, verbose_name='Ativo'),
        ),
        migrations.AddField(
            model_name='itemmo',
            name='status',
            field=models.CharField(
                choices=[('ativo', 'Ativo'), ('pendente', 'Pendente'), ('critico', 'Crítico')],
                default='ativo', max_length=10, verbose_name='Status',
            ),
        ),
        migrations.AlterField(
            model_name='itemmo',
            name='unidade',
            field=models.CharField(
                choices=[('Meses', 'Meses'), ('Dias', 'Dias'), ('Horas', 'Horas'),
                         ('Un', 'Un'), ('Vb', 'Vb'), ('Evento', 'Evento')],
                default='Meses', max_length=10, verbose_name='Unidade',
            ),
        ),
    ]
