from django.db import models
from django.utils import timezone

class Produto(models.Model):
    # AZUL - CADASTRO
    id_planilha = models.IntegerField("ID", primary_key=True)
    nome = models.CharField("Nome", max_length=255)
    modelo = models.CharField("Modelo", max_length=100)
    part_number = models.CharField("P/N", max_length=100, blank=True, null=True)
    fabricante = models.CharField("Fabricante", max_length=100)
    unidade = models.CharField("Unidade", max_length=20)
    categoria = models.CharField("Categoria", max_length=100)
    descricao = models.TextField("Descrição", blank=True, null=True)
    
    # VERDE - CUSTO
    moeda = models.CharField("Moeda", max_length=20) 
    preco_fornecedor = models.DecimalField("Preço Fornecedor", max_digits=12, decimal_places=2)
    unit_reais = models.DecimalField("Unit (Reais)", max_digits=12, decimal_places=2)
    
    # LARANJA - COMPRAS
    frete_na_compra = models.DecimalField("Frete na Compra", max_digits=12, decimal_places=2, default=0)
    ipi = models.DecimalField("IPI (%)", max_digits=5, decimal_places=2, default=0)
    icms = models.DecimalField("ICMS (%)", max_digits=5, decimal_places=2, default=0)
    nome_fornecedor = models.CharField("Nome do Fornecedor", max_length=100)
    estado_origem = models.CharField("Estado de Origem", max_length=5)
    grupo_financeiro = models.CharField("Grupo Financeiro", max_length=50)
    ncm = models.CharField("NCM", max_length=20)
    data_ultima_cotacao = models.DateField("Data da Última Cotação")

    # LILÁS - LUCRO E TRIBUTOS
    lucro_percent = models.DecimalField("Lucro %", max_digits=5, decimal_places=2)
    iss_percent = models.DecimalField("ISS %", max_digits=5, decimal_places=2)
    pis_cofins_percent = models.DecimalField("PIS e COFINS %", max_digits=5, decimal_places=2)
    ir_csll_lp = models.DecimalField("IR e CSLL (LP) %", max_digits=5, decimal_places=2)
    ir_csll_lr = models.DecimalField("IR e CSLL (LR) %", max_digits=5, decimal_places=2)
    mkp = models.DecimalField("MKP", max_digits=5, decimal_places=2)

    # AMARELO - LOCAÇÃO
    custo_loc = models.DecimalField("Custo LOC", max_digits=12, decimal_places=2)
    custo_mensal = models.DecimalField("Custo Mensal", max_digits=12, decimal_places=2)
    iss_loc = models.DecimalField("ISS loc", max_digits=5, decimal_places=2)
    pis_cofins_loc = models.DecimalField("PIS e COFINS LOC", max_digits=5, decimal_places=2)
    ir_csll_lp_loc = models.DecimalField("IR e CSLL (LP) LOC", max_digits=5, decimal_places=2)
    ir_csll_lr_loc = models.DecimalField("IR e CSLL (LR) LOC", max_digits=5, decimal_places=2)
    mkp_loc = models.DecimalField("MKP LOC", max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.id_planilha} - {self.nome}"

class Projeto(models.Model):
    # Opções fixas
    EMPRESAS = [('EMIVE','EMIVE'), ('DIGITAL','DIGITAL'), ('CH','CH'), ('BMSi','BMSi')]
    FATURAMENTO = [('MENSAL','Mensal Recorrente'), ('INSTALACAO','Instalação')]

    id_projeto_manual = models.CharField("ID do Projeto", max_length=50)
    nome_cliente = models.CharField("Nome do Cliente", max_length=255)
    estado_obra = models.CharField("UF", max_length=2)
    municipio_obra = models.CharField("Cidade", max_length=100)
    empresa_executora = models.CharField(max_length=20, choices=EMPRESAS)
    faturamento_servico = models.CharField(max_length=20, choices=FATURAMENTO)
    
    tipo_projeto = models.CharField(max_length=10, default='Privado') # Público ou Privado
    licitacao_publicada = models.BooleanField(default=False)
    material_aplicado = models.BooleanField(default=False)
    
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id_projeto_manual} - {self.nome_cliente}"