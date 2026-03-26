from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    # As colunas que vão aparecer na listagem
    list_display = ('id_planilha', 'nome', 'fabricante', 'categoria', 'preco_fornecedor')
    
    # Barra de busca por nome ou ID
    search_fields = ('nome', 'id_planilha')
    
    # Filtro lateral por categoria ou fabricante
    list_filter = ('categoria', 'fabricante')