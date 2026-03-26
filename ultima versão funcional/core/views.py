from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from .models import Produto, Projeto


# ============================================================
# FAIXAS DE ID POR CATEGORIA (centena de milhar)
# ============================================================
FAIXAS_CATEGORIA = {
    'CFTV':         100000,
    'VMS':          200000,
    'ALARME':       300000,
    'ACESSO':       400000,
    'CABEAMENTO':   500000,
    'INFRA':        600000,
    'REDE':         700000,
    'SWITCHES':     750000,  # Sub-grupo de Rede
    'ENERGIA':      800000,
    'OUTROS':       900000,
    'SERVICOS':    1000000,
}

def gerar_proximo_id(categoria):
    """
    Gera o próximo ID sequencial para uma categoria.
    Ex: CFTV → primeiro produto = 100001, segundo = 100002, etc.
    """
    categoria_upper = categoria.upper().strip()
    
    # Mapeia variações para a chave correta
    mapa = {
        'ACESSO (C.A)': 'ACESSO',
        'ACESSO': 'ACESSO',
        'ELETRICIDADE': 'ENERGIA',
        'SERVIÇO': 'SERVICOS',
        'SERVICO': 'SERVICOS',
    }
    chave = mapa.get(categoria_upper, categoria_upper)
    
    faixa_inicio = FAIXAS_CATEGORIA.get(chave, 900000)  # Default: OUTROS
    faixa_fim = faixa_inicio + 9999
    
    # Busca o maior ID existente nessa faixa
    ultimo = Produto.objects.filter(
        id_planilha__gte=faixa_inicio,
        id_planilha__lte=faixa_fim
    ).order_by('-id_planilha').first()
    
    if ultimo:
        return ultimo.id_planilha + 1
    else:
        return faixa_inicio + 1  # Primeiro da faixa: 100001, 200001, etc.


# ============================================================
# LOGIN
# ============================================================
def minha_tela_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == "POST":
        login_input = request.POST.get('username')
        senha_digitada = request.POST.get('password')

        username_final = login_input
        if "@" in login_input:
            try:
                usuario_pelo_email = User.objects.get(email=login_input)
                username_final = usuario_pelo_email.username
            except User.DoesNotExist:
                pass

        user = authenticate(request, username=username_final, password=senha_digitada)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Usuário/E-mail ou senha incorretos!")
    
    return render(request, 'login.html')


def deslogar(request):
    logout(request)
    return redirect('login')


# ============================================================
# DASHBOARD
# ============================================================
@login_required(login_url='/')
def dashboard(request):
    total_projetos = Projeto.objects.count()
    total_produtos = Produto.objects.count()
    
    # Soma do custo de todos os produtos (unit_reais)
    custo_raw = Produto.objects.aggregate(total=Sum('unit_reais'))['total'] or 0
    
    # Formata para exibição brasileira
    if custo_raw >= 1000000:
        custo_total = f"{custo_raw/1000000:,.1f}M".replace(',', '.')
    elif custo_raw >= 1000:
        custo_total = f"{custo_raw:,.0f}".replace(',', '.')
    else:
        custo_total = f"{custo_raw:,.2f}".replace(',', '.')
    
    context = {
        'total_projetos': total_projetos,
        'total_produtos': total_produtos,
        'custo_total': custo_total,
    }
    return render(request, 'dashboard.html', context)


# ============================================================
# NOVO PROJETO (CREATE)
# ============================================================
@login_required(login_url='/')
def novo_projeto(request):
    if request.method == 'POST':
        try:
            projeto = Projeto.objects.create(
                id_projeto_manual=request.POST.get('id_projeto_manual', ''),
                nome_cliente=request.POST.get('nome_cliente', ''),
                estado_obra=request.POST.get('estado_obra', ''),
                municipio_obra=request.POST.get('municipio_obra', ''),
                empresa_executora=request.POST.get('empresa_executora', 'EMIVE'),
                faturamento_servico=request.POST.get('faturamento_servico', 'MENSAL'),
                tipo_projeto=request.POST.get('tipo_projeto', 'Privado'),
                licitacao_publicada=request.POST.get('licitacao_publicada') == 'true',
                material_aplicado=request.POST.get('material_aplicado') == 'true',
            )
            # Projeto criado → vai direto pro BoM Selector
            return redirect('bom_selector')
        except Exception as e:
            messages.error(request, f'Erro ao criar projeto: {e}')
    
    return render(request, 'novo_projeto.html')


# ============================================================
# CONSULTAR PROJETO (SEARCH)
# ============================================================
@login_required(login_url='/')
def consultar_projeto(request):
    q = request.GET.get('q', '').strip()
    projetos = []
    
    if q:
        projetos = Projeto.objects.filter(
            Q(id_projeto_manual__icontains=q) | Q(nome_cliente__icontains=q)
        ).order_by('-data_criacao')
    
    context = {
        'projetos': projetos,
        'query': q,
    }
    return render(request, 'consultar_projeto.html', context)


# ============================================================
# BOM SELECTOR (lista de produtos para consulta)
# ============================================================
@login_required(login_url='/')
def bom_selector(request):
    categoria = request.GET.get('categoria', '')
    busca = request.GET.get('busca', '')
    
    produtos = Produto.objects.all().order_by('categoria', 'nome')
    
    if categoria:
        produtos = produtos.filter(categoria__iexact=categoria)
    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca) | 
            Q(modelo__icontains=busca) | 
            Q(part_number__icontains=busca) |
            Q(fabricante__icontains=busca)
        )
    
    # Lista de categorias únicas para os filtros
    categorias = Produto.objects.values_list('categoria', flat=True).distinct().order_by('categoria')
    
    context = {
        'produtos': produtos,
        'categorias': categorias,
        'categoria_ativa': categoria,
        'busca': busca,
        'total_produtos': produtos.count(),
    }
    return render(request, 'bom_selector.html', context)


# ============================================================
# CADASTRO DE PRODUTO (CREATE / EDIT)
# ============================================================
@login_required(login_url='/')
def cadastro_produto(request):
    """Tela de cadastro de novo produto."""
    if request.method == 'POST':
        categoria = request.POST.get('categoria', 'OUTROS')
        novo_id = gerar_proximo_id(categoria)
        
        try:
            produto = Produto.objects.create(
                id_planilha=novo_id,
                nome=request.POST.get('nome', ''),
                modelo=request.POST.get('modelo', ''),
                part_number=request.POST.get('part_number', ''),
                fabricante=request.POST.get('fabricante', ''),
                unidade=request.POST.get('unidade', 'peça'),
                categoria=categoria,
                descricao=request.POST.get('descricao', ''),
                moeda=request.POST.get('moeda', 'reais'),
                preco_fornecedor=request.POST.get('preco_fornecedor', 0) or 0,
                unit_reais=request.POST.get('unit_reais', 0) or 0,
                frete_na_compra=request.POST.get('frete_na_compra', 0) or 0,
                ipi=request.POST.get('ipi', 0) or 0,
                icms=request.POST.get('icms', 0) or 0,
                nome_fornecedor=request.POST.get('nome_fornecedor', ''),
                estado_origem=request.POST.get('estado_origem', ''),
                grupo_financeiro=request.POST.get('grupo_financeiro', ''),
                ncm=request.POST.get('ncm', ''),
                data_ultima_cotacao=request.POST.get('data_ultima_cotacao') or None,
                lucro_percent=request.POST.get('lucro_percent', 0) or 0,
                iss_percent=request.POST.get('iss_percent', 0) or 0,
                pis_cofins_percent=request.POST.get('pis_cofins_percent', 0) or 0,
                ir_csll_lp=request.POST.get('ir_csll_lp', 0) or 0,
                ir_csll_lr=request.POST.get('ir_csll_lr', 0) or 0,
                mkp=request.POST.get('mkp', 0) or 0,
                custo_loc=request.POST.get('custo_loc', 0) or 0,
                custo_mensal=request.POST.get('custo_mensal', 0) or 0,
                iss_loc=request.POST.get('iss_loc', 0) or 0,
                pis_cofins_loc=request.POST.get('pis_cofins_loc', 0) or 0,
                ir_csll_lp_loc=request.POST.get('ir_csll_lp_loc', 0) or 0,
                ir_csll_lr_loc=request.POST.get('ir_csll_lr_loc', 0) or 0,
                mkp_loc=request.POST.get('mkp_loc', 0) or 0,
            )
            messages.success(request, f'Produto #{novo_id} - {produto.nome} cadastrado com sucesso!')
            return redirect('bom_selector')
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar produto: {e}')
    
    context = {
        'modo': 'criar',
    }
    return render(request, 'cadastro_produto.html', context)


@login_required(login_url='/')
def detalhe_produto(request, pk):
    """Tela de detalhe/edição de produto existente."""
    produto = get_object_or_404(Produto, pk=pk)
    
    if request.method == 'POST':
        # Modo edição — atualiza os campos
        produto.nome = request.POST.get('nome', produto.nome)
        produto.modelo = request.POST.get('modelo', produto.modelo)
        produto.part_number = request.POST.get('part_number', produto.part_number)
        produto.fabricante = request.POST.get('fabricante', produto.fabricante)
        produto.unidade = request.POST.get('unidade', produto.unidade)
        produto.categoria = request.POST.get('categoria', produto.categoria)
        produto.descricao = request.POST.get('descricao', produto.descricao)
        produto.moeda = request.POST.get('moeda', produto.moeda)
        produto.preco_fornecedor = request.POST.get('preco_fornecedor', produto.preco_fornecedor) or 0
        produto.unit_reais = request.POST.get('unit_reais', produto.unit_reais) or 0
        produto.frete_na_compra = request.POST.get('frete_na_compra', produto.frete_na_compra) or 0
        produto.ipi = request.POST.get('ipi', produto.ipi) or 0
        produto.icms = request.POST.get('icms', produto.icms) or 0
        produto.nome_fornecedor = request.POST.get('nome_fornecedor', produto.nome_fornecedor)
        produto.estado_origem = request.POST.get('estado_origem', produto.estado_origem)
        produto.grupo_financeiro = request.POST.get('grupo_financeiro', produto.grupo_financeiro)
        produto.ncm = request.POST.get('ncm', produto.ncm)
        produto.lucro_percent = request.POST.get('lucro_percent', produto.lucro_percent) or 0
        produto.iss_percent = request.POST.get('iss_percent', produto.iss_percent) or 0
        produto.pis_cofins_percent = request.POST.get('pis_cofins_percent', produto.pis_cofins_percent) or 0
        produto.ir_csll_lp = request.POST.get('ir_csll_lp', produto.ir_csll_lp) or 0
        produto.ir_csll_lr = request.POST.get('ir_csll_lr', produto.ir_csll_lr) or 0
        produto.mkp = request.POST.get('mkp', produto.mkp) or 0
        produto.custo_loc = request.POST.get('custo_loc', produto.custo_loc) or 0
        produto.custo_mensal = request.POST.get('custo_mensal', produto.custo_mensal) or 0
        produto.iss_loc = request.POST.get('iss_loc', produto.iss_loc) or 0
        produto.pis_cofins_loc = request.POST.get('pis_cofins_loc', produto.pis_cofins_loc) or 0
        produto.ir_csll_lp_loc = request.POST.get('ir_csll_lp_loc', produto.ir_csll_lp_loc) or 0
        produto.ir_csll_lr_loc = request.POST.get('ir_csll_lr_loc', produto.ir_csll_lr_loc) or 0
        produto.mkp_loc = request.POST.get('mkp_loc', produto.mkp_loc) or 0
        
        try:
            produto.save()
            messages.success(request, f'Produto #{produto.id_planilha} atualizado com sucesso!')
            return redirect('detalhe_produto', pk=produto.pk)
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {e}')
    
    context = {
        'produto': produto,
        'modo': 'detalhe',  # Começa em modo consulta, JS libera edição
    }
    return render(request, 'cadastro_produto.html', context)


# ============================================================
# GESTÃO DE USUÁRIOS
# ============================================================
@login_required(login_url='/')
def gestao_usuarios(request):
    usuarios = User.objects.all().order_by('username')
    context = {
        'usuarios': usuarios,
    }
    return render(request, 'gestao_usuarios.html', context)
