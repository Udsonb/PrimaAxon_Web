import os
import django
import pandas as pd
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models import Produto

def limpar_v(val, e_porcentagem=False):
    try:
        if pd.isna(val) or val == "" or val == "-": return 0
        if isinstance(val, str):
            val = val.replace('%', '').replace('R$', '').replace(',', '.').strip()
        v_float = float(val)
        if e_porcentagem and 0 < v_float <= 1.0: return v_float * 100
        return v_float
    except: return 0

def importar():
    nome_arquivo = "meus_materiais.xlsx" # Mude se precisar
    if not os.path.exists(nome_arquivo): return print("Arquivo não achado.")
    df = pd.read_excel(nome_arquivo).dropna(subset=['Nome'])

    for _, row in df.iterrows():
        try:
            data_str = row.get('Data da Última Cotação')
            data_final = pd.to_datetime(data_str).date() if pd.notna(data_str) else timezone.now().date()
            
            Produto.objects.update_or_create(
                id_planilha=int(row['ID']),
                defaults={
                    'nome': row.get('Nome'), 'modelo': row.get('Modelo'), 'part_number': row.get('P/N (part Number)'),
                    'fabricante': row.get('Fabricante'), 'unidade': row.get('Unidade'), 'categoria': row.get('Categoria'),
                    'moeda': str(row.get('Moeda', 'reais')).lower(),
                    'preco_fornecedor': limpar_v(row.get('Preço Fornecedor')),
                    'unit_reais': limpar_v(row.get('Unit (Reais)')),
                    'ipi': limpar_v(row.get('IPI'), True), 'icms': limpar_v(row.get('ICMS'), True),
                    'lucro_percent': limpar_v(row.get('Lucro %'), True), 'mkp': limpar_v(row.get('MKP')),
                    # ... (adicione os demais campos se precisar, mas a lógica de decimal já está aqui)
                }
            )
            print(f"✅ ID {row['ID']} OK.")
        except Exception as e: print(f"❌ Erro ID {row.get('ID')}: {e}")

if __name__ == "__main__": importar()