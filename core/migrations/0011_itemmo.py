from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_projeto_revisao'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemMO',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aba', models.CharField(choices=[('operacional', 'Mão de Obra'), ('ferramentas', 'Equipamentos/Insumos'), ('transporte', 'Transporte'), ('demais_custos', 'Demais Custos'), ('terceiros', 'Terceirizados')], max_length=20)),
                ('descricao', models.CharField(max_length=255, verbose_name='Descrição')),
                ('quantidade', models.DecimalField(decimal_places=2, default=1, max_digits=10, verbose_name='Quantidade')),
                ('tempo', models.DecimalField(decimal_places=2, default=1, max_digits=10, verbose_name='Tempo')),
                ('unidade', models.CharField(choices=[('Meses', 'Meses'), ('Dias', 'Dias'), ('Horas', 'Horas'), ('Un', 'Un'), ('Vb', 'Vb')], default='Meses', max_length=10, verbose_name='Unidade')),
                ('custo_unitario', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='Custo Unitário')),
                ('projeto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens_mo', to='core.projeto')),
            ],
        ),
    ]
