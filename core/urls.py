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
    path('projeto/<int:projeto_id>/exportar/', views.exportar_projeto, name='exportar_projeto'),
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
    path('trocar-senha/', views.trocar_senha_proprio, name='trocar_senha_proprio'),
    path('projeto/<int:projeto_id>/mo/', views.entrar_mo, name='entrar_mo'),
    path('projeto/<int:projeto_id>/mo/<str:aba>/', views.gestao_mo, name='gestao_mo'),
    path('dash/gerencial/', views.dash_gerencial, name='dash_gerencial'),
    path('dash/analista/', views.dash_analista, name='dash_analista'),
    path('dash/orcamentista/', views.dash_orcamentista, name='dash_orcamentista'),
    path('validacao/', views.validacao_orcamento, name='validacao_orcamento'),
    path('estrategia/', views.estrategia_financeira, name='estrategia_financeira'),
    path('produtos/template/', views.template_importacao_produtos, name='template_importacao_produtos'),
    path('produtos/importar/', views.importar_produtos_excel, name='importar_produtos_excel'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
