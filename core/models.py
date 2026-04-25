import os, re, uuid
from django.db import models
from django.utils import timezone


def _upload_usuario(instance, filename):
    ext = os.path.splitext(filename)[1].lower() or '.jpg'
    safe = re.sub(r'[^a-zA-Z0-9]', '_', os.path.splitext(filename)[0])[:40]
    return f'usuarios/{safe}_{uuid.uuid4().hex[:8]}{ext}'


def _upload_logo(instance, filename):
    ext = os.path.splitext(filename)[1].lower() or '.png'
    safe = re.sub(r'[^a-zA-Z0-9]', '_', os.path.splitext(filename)[0])[:40]
    return f'logos/{safe}_{uuid.uuid4().hex[:8]}{ext}'


def _upload_produto(instance, filename):
    ext = os.path.splitext(filename)[1].lower() or '.jpg'
    safe = re.sub(r'[^a-zA-Z0-9]', '_', os.path.splitext(filename)[0])[:40]
    return f'produtos/{safe}_{uuid.uuid4().hex[:8]}{ext}'


class Empresa(models.Model):
    razao_social = models.CharField("Razão Social", max_length=255)
    nome_fantasia = models.CharField("Nome Fantasia", max_length=255)
    cnpj = models.CharField("CNPJ", max_length=20, unique=True)
    logo = models.ImageField("Logo", upload_to=_upload_logo, blank=True, null=True)
    is_sistema = models.BooleanField("Empresa do Sistema", default=False,
        help_text="Marque se esta é a Prisma Axon System (não aparece na combo do login)")

    def __str__(self):
        return self.nome_fantasia


class Perfil(models.Model):
    CARGO_CHOICES = [
        ('diretor_geral',     'Diretor Geral'),
        ('diretor_setor',     'Diretor de Setor'),
        ('gerente_pre_vendas','Gerente Pré-Vendas'),
        ('supervisor',        'Supervisor'),
        ('gerente_comercial', 'Gerente Comercial'),
        ('executivo',         'Executivo'),
        ('analista',          'Analista'),
        ('gerente_compras',   'Gerente de Compras'),
        ('comprador',         'Comprador'),
        ('orcamentista',      'Orçamentista'),
    ]

    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='perfil')
    foto = models.ImageField("Foto", upload_to=_upload_usuario, blank=True, null=True)
    funcao = models.CharField("Função", max_length=100, blank=True)
    cargo = models.CharField("Cargo", max_length=30, choices=CARGO_CHOICES, default='analista')
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"


class Produto(models.Model):
    STATUS_CHOICES = [
        ('verde', 'OK'),
        ('amarelo', 'Aguardando Validação'),
        ('azul', 'Validado'),
        ('vermelho', 'Descontinuado'),
    ]

    # AZUL - CADASTRO
    id_planilha = models.IntegerField("ID", primary_key=True)
    nome = models.CharField("Nome", max_length=255)
    modelo = models.CharField("Modelo", max_length=500)
    part_number = models.CharField("P/N", max_length=500, blank=True, null=True)
    fabricante = models.CharField("Fabricante", max_length=100)
    unidade = models.CharField("Unidade", max_length=20)
    categoria = models.CharField("Categoria", max_length=100)
    descricao = models.TextField("Descrição", blank=True, null=True)
    status = models.CharField("Status", max_length=10, choices=STATUS_CHOICES, default='verde')
    foto = models.ImageField("Foto do Produto", upload_to=_upload_produto, blank=True, null=True)
    preco_variavel = models.BooleanField("Preço Variável (M.O)", default=False,
        help_text="Marque se o preço deste item é definido pela Mão de Obra do projeto")
    
    # VERDE - CUSTO
    moeda = models.CharField("Moeda", max_length=20) 
    preco_fornecedor = models.DecimalField("Preço Fornecedor", max_digits=12, decimal_places=2)
    unit_reais = models.DecimalField("Unit (Reais)", max_digits=12, decimal_places=2)
    
    # LARANJA - COMPRAS
    frete_na_compra = models.DecimalField("Frete na Compra", max_digits=12, decimal_places=2, default=0)
    ipi = models.DecimalField("IPI (%)", max_digits=5, decimal_places=2, default=0)
    icms = models.DecimalField("ICMS (%)", max_digits=5, decimal_places=2, default=0)
    nome_fornecedor = models.CharField("Nome do Fornecedor", max_length=1000)
    estado_origem = models.CharField("Estado de Origem", max_length=100)
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
    EMPRESAS = [('EMIVE','EMIVE'), ('DIGITAL','DIGITAL'), ('CH','CH'), ('BMSi','BMSi')]
    FATURAMENTO = [('MENSAL','Mensal Recorrente'), ('INSTALACAO','Instalação')]

    id_projeto_manual = models.CharField("ID do Projeto", max_length=50, unique=True)
    nome_cliente = models.CharField("Nome do Cliente", max_length=255)
    estado_obra = models.CharField("UF", max_length=2)
    municipio_obra = models.CharField("Cidade", max_length=100)
    empresa_executora = models.CharField(max_length=20, choices=EMPRESAS)
    faturamento_servico = models.CharField(max_length=20, choices=FATURAMENTO)
    
    tipo_projeto = models.CharField(max_length=10, default='Privado')
    licitacao_publicada = models.BooleanField(default=False)
    material_aplicado = models.BooleanField(default=False)
    finalizado = models.BooleanField("Projeto finalizado", default=False)
    
    revisao = models.IntegerField("Revisão", default=0)
    data_criacao = models.DateTimeField(auto_now_add=True)

    @property
    def revisao_label(self):
        return f"REV.{self.revisao:02d}"

    def __str__(self):
        return f"{self.id_projeto_manual} - {self.nome_cliente}"


class ItemProjeto(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.IntegerField("Quantidade", default=1)
    preco_unitario = models.DecimalField("Preço Unitário", max_digits=12, decimal_places=2)
    faturar_servico = models.BooleanField("Faturar como Serviço", default=False)
    data_inclusao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('projeto', 'produto')

    @property
    def valor_total(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.produto.nome} x{self.quantidade}"


class ItemMO(models.Model):
    ABA_CHOICES = [
        ('operacional', 'Mão de Obra'),
        ('ferramentas', 'Equipamentos/Insumos'),
        ('transporte', 'Transporte'),
        ('demais_custos', 'Demais Custos'),
        ('terceiros', 'Terceirizados'),
    ]
    UNIDADE_CHOICES = [
        ('Meses', 'Meses'), ('Dias', 'Dias'), ('Horas', 'Horas'),
        ('Un', 'Un'), ('Vb', 'Vb'), ('Evento', 'Evento'),
    ]
    STATUS_CHOICES = [
        ('ativo', 'Ativo'), ('pendente', 'Pendente'), ('critico', 'Crítico'),
    ]

    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='itens_mo')
    aba = models.CharField(max_length=20, choices=ABA_CHOICES)
    descricao = models.CharField("Descrição", max_length=255)
    especificacao = models.CharField("Especificação", max_length=255, blank=True, default='')
    quantidade = models.DecimalField("Quantidade", max_digits=10, decimal_places=2, default=1)
    tempo = models.DecimalField("Tempo", max_digits=10, decimal_places=2, default=1)
    unidade = models.CharField("Unidade", max_length=10, choices=UNIDADE_CHOICES, default='Meses')
    custo_unitario = models.DecimalField("Custo Unitário", max_digits=14, decimal_places=2, default=0)
    ativo = models.BooleanField("Ativo", default=True)
    status = models.CharField("Status", max_length=10, choices=STATUS_CHOICES, default='ativo')

    @property
    def custo_total(self):
        return self.quantidade * self.tempo * self.custo_unitario

    def __str__(self):
        return f"{self.projeto.id_projeto_manual} - {self.aba} - {self.descricao}"
