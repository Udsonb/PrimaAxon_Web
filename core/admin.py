from django.contrib import admin
from .models import Produto, Empresa, Projeto, ItemProjeto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id_planilha', 'nome', 'fabricante', 'categoria', 'preco_fornecedor', 'status')
    search_fields = ('nome', 'id_planilha')
    list_filter = ('categoria', 'fabricante', 'status')

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome_fantasia', 'razao_social', 'cnpj', 'is_sistema')
    search_fields = ('nome_fantasia', 'razao_social', 'cnpj')
    list_filter = ('is_sistema',)

class ItemProjetoInline(admin.TabularInline):
    model = ItemProjeto
    extra = 0
    readonly_fields = ('data_inclusao',)

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('id_projeto_manual', 'nome_cliente', 'empresa_executora', 'finalizado', 'data_criacao')
    search_fields = ('id_projeto_manual', 'nome_cliente')
    list_filter = ('finalizado', 'empresa_executora')
    inlines = [ItemProjetoInline]
