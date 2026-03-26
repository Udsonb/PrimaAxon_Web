from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth
    path('', views.minha_tela_login, name='login'),
    path('sair/', views.deslogar, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Projetos
    path('projeto/novo/', views.novo_projeto, name='novo_projeto'),
    path('projeto/consultar/', views.consultar_projeto, name='consultar_projeto'),
    
    # Produtos
    path('produto/cadastro/', views.cadastro_produto, name='cadastro_produto'),
    path('produto/<int:pk>/', views.detalhe_produto, name='detalhe_produto'),
    path('catalogo/', views.bom_selector, name='bom_selector'),
    
    # Gestão
    path('gestao/usuarios/', views.gestao_usuarios, name='gestao_usuarios'),
]
