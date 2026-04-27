from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_configuracaofinanceira'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PedidoExclusaoProduto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('justificativa', models.TextField(verbose_name='Justificativa')),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('aprovado', 'Aprovado'), ('rejeitado', 'Rejeitado')], default='pendente', max_length=10)),
                ('data_solicitacao', models.DateTimeField(auto_now_add=True)),
                ('data_avaliacao', models.DateTimeField(blank=True, null=True)),
                ('motivo_rejeicao', models.TextField(blank=True, verbose_name='Motivo da Rejeição')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos_exclusao', to='core.produto')),
                ('solicitante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos_exclusao', to=settings.AUTH_USER_MODEL)),
                ('avaliador', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exclusoes_avaliadas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-data_solicitacao'],
            },
        ),
    ]
