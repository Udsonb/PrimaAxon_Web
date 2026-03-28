from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('status/', views.status_diagnostico, name='status'),
    path('', views.minha_tela_login, name='login'),
    path('sair/', views.deslogar, name='logout'),
    path('inicio/', views.inicio, name='inicio'),
    path('projeto/novo/', views.novo_projeto, name='novo_projeto'),
    path('projeto/consultar/', views.consultar_projeto, name='consultar_projeto'),
    path('projeto/<int:projeto_id>/cancelar/', views.cancelar_projeto, name='cancelar_projeto'),
    path('projeto/<int:projeto_id>/bom/', views.bom_selector, name='bom_selector_projeto'),
    path('projeto/<int:projeto_id>/fluxo/', views.fluxo_projeto, name='fluxo_projeto'),
    path('catalogo/', views.bom_selector, name='bom_selector'),
    path('produto/cadastro/', views.cadastro_produto, name='cadastro_produto'),
    path('produto/<int:pk>/', views.detalhe_produto, name='detalhe_produto'),
    path('produto/<int:pk>/aba/<str:aba>/', views.produto_aba, name='produto_aba'),
    path('gestao/usuarios/', views.gestao_usuarios, name='gestao_usuarios'),
    path('gestao/usuarios/novo/', views.cadastro_usuario, name='cadastro_usuario'),
    path('gestao/usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('gestao/empresas/', views.gestao_empresas, name='gestao_empresas'),
    path('gestao/empresas/nova/', views.cadastro_empresa, name='cadastro_empresa'),
    path('gestao/empresas/<int:empresa_id>/editar/', views.editar_empresa, name='editar_empresa'),
    path('gestao/usuarios/<int:user_id>/reset-senha/', views.reset_senha_usuario, name='reset_senha_usuario'),
    path('gestao/programa/', views.gestao_programa, name='gestao_programa'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
