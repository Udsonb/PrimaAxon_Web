from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from .models import Produto, Projeto, Empresa, Perfil, ItemProjeto


FAIXAS_CATEGORIA = {
    'CFTV': 100000, 'VMS': 200000, 'ALARME': 300000, 'ACESSO': 400000,
    'CABEAMENTO': 500000, 'INFRA': 600000, 'REDE': 700000, 'SWITCHES': 750000,
    'ENERGIA': 800000, 'OUTROS': 900000, 'SERVICOS': 1000000,
}

def gerar_proximo_id(categoria):
    categoria_upper = categoria.upper().strip()
    mapa = {'ACESSO (C.A)': 'ACESSO', 'ELETRICIDADE': 'ENERGIA', 'SERVIÇO': 'SERVICOS', 'SERVICO': 'SERVICOS'}
    chave = mapa.get(categoria_upper, categoria_upper)
    faixa_inicio = FAIXAS_CATEGORIA.get(chave, 900000)
    ultimo = Produto.objects.filter(id_planilha__gte=faixa_inicio, id_planilha__lte=faixa_inicio+9999).order_by('-id_planilha').first()
    return (ultimo.id_planilha + 1) if ultimo else (faixa_inicio + 1)


# ============================================================
# LOGIN
# ============================================================
def minha_tela_login(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    if request.method == "POST":
        login_input = request.POST.get('username')
        senha_digitada = request.POST.get('password')
        empresa_id = request.POST.get('company', '')
        username_final = login_input
        if "@" in login_input:
            try:
                username_final = User.objects.get(email=login_input).username
            except User.DoesNotExist:
                pass
        user = authenticate(request, username=username_final, password=senha_digitada)
        if user is not None:
            login(request, user)
            # Salva a empresa na sessão DEPOIS do login e força persistência
            if empresa_id:
                request.session['empresa_id'] = int(empresa_id)
                request.session.modified = True
                request.session.save()
            return redirect('inicio')
        else:
            messages.error(request, "Usuário/E-mail ou senha incorretos!")
    empresas = Empresa.objects.all().order_by('nome_fantasia')
    return render(request, 'login.html', {'empresas': empresas})


def deslogar(request):
    logout(request)
    return redirect('login')


# ============================================================
# INÍCIO (tela principal)
# ============================================================
@login_required(login_url='/')
def inicio(request):
    total_projetos = Projeto.objects.filter(finalizado=True).count()
    total_produtos = Produto.objects.count()
    # Soma real dos projetos finalizados
    from decimal import Decimal
    valor_total_projetos = Decimal('0')
    for projeto in Projeto.objects.filter(finalizado=True):
        for item in ItemProjeto.objects.filter(projeto=projeto):
            valor_total_projetos += item.preco_unitario * item.quantidade
    # Formatar
    if valor_total_projetos >= 1000000:
        valor_fmt = f"{float(valor_total_projetos)/1000000:,.1f}M".replace(',', '.')
    elif valor_total_projetos >= 1000:
        valor_fmt = f"{float(valor_total_projetos):,.2f}".replace(',', 'X').replace('.', '.').replace('X', ',')
    else:
        valor_fmt = f"{float(valor_total_projetos):,.2f}".replace(',', 'X').replace('.', '.').replace('X', ',')
    context = {
        'total_projetos': total_projetos,
        'total_produtos': total_produtos,
        'valor_total_projetos': valor_fmt,
    }
    return render(request, 'inicio.html', context)


# ============================================================
# PRÉ-PROJETO (wizard etapa 1)
# ============================================================
@login_required(login_url='/')
def novo_projeto(request):
    if request.method == 'POST':
        id_manual = request.POST.get('id_projeto_manual', '').strip()
        if not id_manual:
            messages.error(request, 'O ID do projeto é obrigatório.')
            return render(request, 'novo_projeto.html')
        if Projeto.objects.filter(id_projeto_manual=id_manual).exists():
            messages.error(request, f'Já existe um projeto com o número "{id_manual}". Escolha outro.')
            return render(request, 'novo_projeto.html')
        try:
            projeto = Projeto.objects.create(
                id_projeto_manual=id_manual,
                nome_cliente=request.POST.get('nome_cliente', ''),
                estado_obra=request.POST.get('estado_obra', ''),
                municipio_obra=request.POST.get('municipio_obra', ''),
                empresa_executora=request.POST.get('empresa_executora', 'EMIVE'),
                faturamento_servico=request.POST.get('faturamento_servico', 'MENSAL'),
                tipo_projeto=request.POST.get('tipo_projeto', 'Privado'),
                licitacao_publicada=request.POST.get('licitacao_publicada') == 'true',
                finalizado=False,
            )
            return redirect('bom_selector_projeto', projeto_id=projeto.id)
        except Exception as e:
            messages.error(request, f'Erro ao criar pré-projeto: {e}')
    
    # Pega empresa da sessão para pré-selecionar
    empresa_logada = None
    try:
        empresa_id = request.session.get('empresa_id')
        if empresa_id:
            empresa_logada = Empresa.objects.get(id=empresa_id).nome_fantasia
    except Exception:
        pass
    return render(request, 'novo_projeto.html', {'empresa_logada': empresa_logada})


# ============================================================
# CONSULTAR PROJETO (mostra todos se sem filtro)
# ============================================================
@login_required(login_url='/')
def consultar_projeto(request):
    # Excluir projeto
    if request.method == 'POST':
        projeto_id = request.POST.get('excluir_projeto_id')
        if projeto_id:
            try:
                projeto = Projeto.objects.get(id=projeto_id)
                ItemProjeto.objects.filter(projeto=projeto).delete()
                projeto.delete()
            except Projeto.DoesNotExist:
                pass
        return redirect('consultar_projeto')

    q = request.GET.get('q', '').strip()
    if q:
        projetos = Projeto.objects.filter(
            Q(id_projeto_manual__icontains=q) | Q(nome_cliente__icontains=q)
        ).order_by('-data_criacao')
    else:
        projetos = Projeto.objects.all().order_by('-data_criacao')

    # Calcular totais para cada projeto
    projetos_dados = []
    for p in projetos:
        itens = ItemProjeto.objects.filter(projeto=p)
        custo = sum(float(i.preco_unitario) * i.quantidade for i in itens)
        tem_itens = itens.exists()
        projetos_dados.append({
            'projeto': p,
            'custo': custo,
            'venda': custo,  # TODO: aplicar MKP
            'tem_itens': tem_itens,
        })

    return render(request, 'consultar_projeto.html', {'projetos_dados': projetos_dados, 'query': q, 'total': len(projetos_dados)})


# ============================================================
# BOM SELECTOR
# ============================================================
@login_required(login_url='/')
def bom_selector(request, projeto_id=None):
    projeto = get_object_or_404(Projeto, id=projeto_id) if projeto_id else None

    # POST = incluir itens no projeto
    if request.method == 'POST' and projeto:
        produto_ids = request.POST.getlist('produto_ids')
        qtds = request.POST.getlist('qtds')
        count = 0
        for pid, qty in zip(produto_ids, qtds):
            try:
                produto = Produto.objects.get(pk=int(pid))
                ItemProjeto.objects.update_or_create(
                    projeto=projeto, produto=produto,
                    defaults={
                        'quantidade': int(qty) if qty else 1,
                        'preco_unitario': produto.unit_reais,
                    }
                )
                count += 1
            except (Produto.DoesNotExist, ValueError):
                pass

        finalizar = request.POST.get('finalizar') == '1'
        if finalizar:
            return redirect('fluxo_projeto', projeto_id=projeto.id)

    categoria = request.GET.get('categoria', '')
    busca = request.GET.get('busca', '')
    produtos = Produto.objects.all().order_by('categoria', 'nome')

    # Excluir produtos já incluídos neste projeto
    if projeto:
        ids_ja_incluidos = ItemProjeto.objects.filter(projeto=projeto).values_list('produto_id', flat=True)
        produtos = produtos.exclude(id_planilha__in=ids_ja_incluidos)

    if categoria:
        produtos = produtos.filter(categoria__iexact=categoria)
    if busca:
        produtos = produtos.filter(
            Q(nome__icontains=busca) | Q(modelo__icontains=busca) |
            Q(part_number__icontains=busca) | Q(fabricante__icontains=busca)
        )
    categorias = Produto.objects.values_list('categoria', flat=True).distinct().order_by('categoria')

    # Totais já incluídos no projeto
    total_itens_projeto = 0
    custo_projeto = 0
    if projeto:
        itens_projeto = ItemProjeto.objects.filter(projeto=projeto)
        total_itens_projeto = itens_projeto.count()
        custo_projeto = sum(i.preco_unitario * i.quantidade for i in itens_projeto)

    context = {
        'produtos': produtos, 'categorias': categorias,
        'categoria_ativa': categoria, 'busca': busca,
        'total_produtos': produtos.count(), 'projeto': projeto,
        'total_itens_projeto': total_itens_projeto,
        'custo_projeto': custo_projeto,
    }
    return render(request, 'bom_selector.html', context)


# ============================================================
# FLUXO DO PROJETO (tela final do BoM construído)
# ============================================================
@login_required(login_url='/')
def fluxo_projeto(request, projeto_id):
    projeto = get_object_or_404(Projeto, id=projeto_id)

    if request.method == 'POST':
        acao = request.POST.get('acao', '')

        # Excluir item
        if acao == 'excluir':
            item_id = request.POST.get('item_id')
            ItemProjeto.objects.filter(id=item_id, projeto=projeto).delete()
            return redirect('fluxo_projeto', projeto_id=projeto.id)

        # Salvar quantidades
        if acao == 'salvar_qtds':
            for item in ItemProjeto.objects.filter(projeto=projeto):
                nova_qty = request.POST.get(f'qty_{item.id}')
                if nova_qty:
                    item.quantidade = int(nova_qty)
                    item.save()
            return redirect('fluxo_projeto', projeto_id=projeto.id)

        # Finalizar projeto
        if acao == 'finalizar':
            # Salvar quantidades primeiro
            for item in ItemProjeto.objects.filter(projeto=projeto):
                nova_qty = request.POST.get(f'qty_{item.id}')
                if nova_qty:
                    item.quantidade = int(nova_qty)
                    item.save()
            # Aplicar desconto se houver
            desconto = request.POST.get('desconto', '0')
            # Marcar como finalizado
            projeto.finalizado = True
            projeto.save()
            return redirect('inicio')

    itens = ItemProjeto.objects.filter(projeto=projeto).select_related('produto')

    total_materiais = 0
    total_servico = 0
    for item in itens:
        valor = item.preco_unitario * item.quantidade
        if item.faturar_servico:
            total_servico += valor
        else:
            total_materiais += valor

    custo_total = total_materiais + total_servico
    venda_total = custo_total  # TODO: aplicar MKP

    context = {
        'projeto': projeto,
        'itens': itens,
        'total_materiais': total_materiais,
        'total_servico': total_servico,
        'custo_total': custo_total,
        'venda_total': venda_total,
    }
    return render(request, 'fluxo_projeto.html', context)


# ============================================================
# CANCELAR PRÉ-PROJETO
# ============================================================
@login_required(login_url='/')
def cancelar_projeto(request, projeto_id):
    projeto = get_object_or_404(Projeto, id=projeto_id)
    if not projeto.finalizado:
        projeto.delete()
    return redirect('inicio')


# ============================================================
# CADASTRO DE PRODUTO
# ============================================================
@login_required(login_url='/')
def cadastro_produto(request):
    if request.method == 'POST':
        categoria = request.POST.get('categoria', 'OUTROS')
        novo_id = gerar_proximo_id(categoria)
        try:
            Produto.objects.create(
                id_planilha=novo_id, nome=request.POST.get('nome', ''),
                modelo=request.POST.get('modelo', ''), part_number=request.POST.get('part_number', ''),
                fabricante=request.POST.get('fabricante', ''), unidade=request.POST.get('unidade', 'peça'),
                categoria=categoria, descricao=request.POST.get('descricao', ''),
                moeda=request.POST.get('moeda', 'reais'),
                preco_fornecedor=request.POST.get('preco_fornecedor', 0) or 0,
                unit_reais=request.POST.get('unit_reais', 0) or 0,
                frete_na_compra=request.POST.get('frete_na_compra', 0) or 0,
                ipi=request.POST.get('ipi', 0) or 0, icms=request.POST.get('icms', 0) or 0,
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
                status='amarelo',  # Novo produto = aguardando validação
            )
            return redirect('inicio')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
    return render(request, 'cadastro_produto.html', {'modo': 'criar'})


@login_required(login_url='/')
def detalhe_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        for field in ['nome','modelo','part_number','fabricante','unidade','categoria','descricao','moeda',
                       'nome_fornecedor','estado_origem','grupo_financeiro','ncm']:
            setattr(produto, field, request.POST.get(field, getattr(produto, field)))
        for field in ['preco_fornecedor','unit_reais','frete_na_compra','ipi','icms',
                       'lucro_percent','iss_percent','pis_cofins_percent','ir_csll_lp','ir_csll_lr','mkp',
                       'custo_loc','custo_mensal','iss_loc','pis_cofins_loc','ir_csll_lp_loc','ir_csll_lr_loc','mkp_loc']:
            setattr(produto, field, request.POST.get(field, getattr(produto, field)) or 0)
        try:
            produto.save()
            return redirect('detalhe_produto', pk=produto.pk)
        except Exception as e:
            messages.error(request, f'Erro: {e}')
    return render(request, 'cadastro_produto.html', {'produto': produto, 'modo': 'detalhe'})


# ============================================================
# GESTÃO DE USUÁRIOS
# ============================================================
@login_required(login_url='/')
def gestao_usuarios(request):
    usuarios = User.objects.all().order_by('username')
    return render(request, 'gestao_usuarios.html', {'usuarios': usuarios})


# ============================================================
# GESTÃO DE EMPRESAS
# ============================================================
@login_required(login_url='/')
def gestao_empresas(request):
    empresas = Empresa.objects.all().order_by('nome_fantasia')
    return render(request, 'gestao_empresas.html', {'empresas': empresas})


@login_required(login_url='/')
def cadastro_empresa(request):
    if request.method == 'POST':
        cnpj = request.POST.get('cnpj', '').strip()
        if Empresa.objects.filter(cnpj=cnpj).exists():
            messages.error(request, f'Já existe uma empresa com o CNPJ "{cnpj}".')
            return render(request, 'cadastro_empresa.html')
        try:
            empresa = Empresa(
                razao_social=request.POST.get('razao_social', ''),
                nome_fantasia=request.POST.get('nome_fantasia', ''),
                cnpj=cnpj,
            )
            if request.FILES.get('logo'):
                empresa.logo = request.FILES['logo']
            empresa.save()
            return redirect('gestao_empresas')
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar empresa: {e}')
    return render(request, 'cadastro_empresa.html')


@login_required(login_url='/')
def editar_empresa(request, empresa_id):
    edit_empresa = get_object_or_404(Empresa, id=empresa_id)
    if request.method == 'POST':
        edit_empresa.razao_social = request.POST.get('razao_social', edit_empresa.razao_social)
        edit_empresa.nome_fantasia = request.POST.get('nome_fantasia', edit_empresa.nome_fantasia)
        if request.FILES.get('logo'):
            edit_empresa.logo = request.FILES['logo']
        try:
            edit_empresa.save()
            return redirect('gestao_empresas')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
    return render(request, 'cadastro_empresa.html', {'edit_empresa': edit_empresa})


# ============================================================
# CADASTRO / EDIÇÃO DE USUÁRIO
# ============================================================
@login_required(login_url='/')
def cadastro_usuario(request):
    empresas = Empresa.objects.all().order_by('nome_fantasia')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not username:
            messages.error(request, 'Nome de usuário é obrigatório.')
            return render(request, 'cadastro_usuario.html', {'empresas': empresas})
        if User.objects.filter(username=username).exists():
            messages.error(request, f'O nome de usuário "{username}" já existe.')
            return render(request, 'cadastro_usuario.html', {'empresas': empresas})
        if password != password2:
            messages.error(request, 'As senhas não conferem.')
            return render(request, 'cadastro_usuario.html', {'empresas': empresas})
        if len(password) < 4:
            messages.error(request, 'A senha deve ter pelo menos 4 caracteres.')
            return render(request, 'cadastro_usuario.html', {'empresas': empresas})

        try:
            nivel = request.POST.get('nivel', 'analista')
            user = User.objects.create_user(
                username=username, email=email, password=password,
                first_name=first_name, last_name=last_name,
            )
            if nivel == 'admin':
                user.is_superuser = True
                user.is_staff = True
            elif nivel in ('gerente', 'supervisor'):
                user.is_staff = True
            user.save()

            # Criar perfil com foto e função
            empresa_id = request.POST.get('empresa', '')
            perfil = Perfil.objects.create(
                user=user,
                funcao=request.POST.get('funcao', ''),
                empresa_id=int(empresa_id) if empresa_id else None,
            )
            if request.FILES.get('foto'):
                perfil.foto = request.FILES['foto']
                perfil.save()

            return redirect('gestao_usuarios')
        except Exception as e:
            messages.error(request, f'Erro ao criar usuário: {e}')

    return render(request, 'cadastro_usuario.html', {'empresas': empresas})


@login_required(login_url='/')
def editar_usuario(request, user_id):
    edit_user = get_object_or_404(User, id=user_id)
    empresas = Empresa.objects.all().order_by('nome_fantasia')

    # Garantir que o perfil existe
    perfil, _ = Perfil.objects.get_or_create(user=edit_user)

    if request.method == 'POST':
        edit_user.first_name = request.POST.get('first_name', edit_user.first_name)
        edit_user.last_name = request.POST.get('last_name', edit_user.last_name)
        edit_user.email = request.POST.get('email', edit_user.email)

        nivel = request.POST.get('nivel', 'analista')
        edit_user.is_superuser = (nivel == 'admin')
        edit_user.is_staff = (nivel in ('admin', 'gerente', 'supervisor'))

        perfil.funcao = request.POST.get('funcao', perfil.funcao)
        empresa_id = request.POST.get('empresa', '')
        perfil.empresa_id = int(empresa_id) if empresa_id else None

        if request.FILES.get('foto'):
            perfil.foto = request.FILES['foto']

        try:
            edit_user.save()
            perfil.save()
            return redirect('gestao_usuarios')
        except Exception as e:
            messages.error(request, f'Erro: {e}')

    return render(request, 'cadastro_usuario.html', {'edit_user': edit_user, 'perfil': perfil, 'empresas': empresas})


# ============================================================
# PRODUTO — ABAS DETALHADAS
# ============================================================
@login_required(login_url='/')
def produto_aba(request, pk, aba):
    produto = get_object_or_404(Produto, pk=pk)

    CAMPOS_TEXTO = {
        'cadastro': ['nome', 'modelo', 'part_number', 'fabricante', 'unidade', 'categoria', 'descricao'],
        'fiscal':   ['moeda'],
        'compras':  ['nome_fornecedor', 'estado_origem', 'grupo_financeiro', 'ncm'],
        'mkp':      [],
        'locacao':  [],
    }
    CAMPOS_DEC = {
        'cadastro': [],
        'fiscal':   ['preco_fornecedor', 'unit_reais', 'frete_na_compra', 'ipi', 'icms'],
        'compras':  [],
        'mkp':      ['lucro_percent', 'iss_percent', 'pis_cofins_percent', 'ir_csll_lp', 'ir_csll_lr', 'mkp'],
        'locacao':  ['custo_loc', 'custo_mensal', 'iss_loc', 'pis_cofins_loc', 'ir_csll_lp_loc', 'ir_csll_lr_loc', 'mkp_loc'],
    }
    TEMPLATES = {
        'cadastro': 'cadastro_produtos_inclusao.html',
        'fiscal':   'cadastro_produtos_fiscal.html',
        'compras':  'cadastro_produtos_compras.html',
        'mkp':      'cadastro_produtos_mkp.html',
        'locacao':  'cadastro_produtos_mkp_locacao.html',
    }

    if aba not in TEMPLATES:
        from django.http import Http404
        raise Http404

    if request.method == 'POST':
        for field in CAMPOS_TEXTO.get(aba, []):
            val = request.POST.get(field, '').strip()
            setattr(produto, field, val)
        for field in CAMPOS_DEC.get(aba, []):
            val = request.POST.get(field)
            setattr(produto, field, val or 0)
        if aba == 'compras':
            dt = request.POST.get('data_ultima_cotacao')
            if dt:
                produto.data_ultima_cotacao = dt
        if aba == 'cadastro':
            produto.preco_variavel = request.POST.get('preco_variavel') == 'on'
            if request.FILES.get('foto'):
                produto.foto = request.FILES['foto']
        try:
            produto.save()
            messages.success(request, 'Dados salvos.')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
        return redirect('produto_aba', pk=pk, aba=aba)

    return render(request, TEMPLATES[aba], {'produto': produto, 'aba': aba})


# ============================================================
# DIAGNÓSTICO (sem login — apenas para verificar o sistema)
# ============================================================
from django.http import JsonResponse

def status_diagnostico(request):
    from django.conf import settings
    import os, json, tempfile
    from django.core.management import call_command

    fixture_path = os.path.join(settings.BASE_DIR, 'fixtures', 'initial_data.json')
    fixture_existe = os.path.exists(fixture_path)

    # Upload de logos via ?upload=1
    upload_resultado = None
    if request.GET.get('upload') == '1':
        try:
            from django.core.management import call_command as _cc
            _cc('upload_media_to_gcs', verbosity=0)
            upload_resultado = 'OK'
        except Exception as e:
            upload_resultado = f'ERRO: {e}'

    # Carga de produtos via ?load_products=1
    carga_produtos_resultado = None
    if request.GET.get('load_products') == '1' and fixture_existe:
        try:
            if Produto.objects.exists():
                carga_produtos_resultado = f'Produtos já existem ({Produto.objects.count()}), ignorado'
            else:
                # Carrega apenas os modelos que ainda não existem
                ONLY_PRODUCTS = {'core.produto', 'core.projeto', 'core.itemprojeto'}
                with open(fixture_path, encoding='utf-8') as f:
                    all_data = json.load(f)
                products_data = [o for o in all_data if o['model'] in ONLY_PRODUCTS]
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                                 delete=False, encoding='utf-8') as tmp:
                    json.dump(products_data, tmp, ensure_ascii=False)
                    tmp_path = tmp.name
                try:
                    call_command('loaddata', tmp_path, verbosity=0)
                    carga_produtos_resultado = f'OK — {Produto.objects.count()} produtos carregados'
                finally:
                    os.unlink(tmp_path)
        except Exception as e:
            carga_produtos_resultado = f'ERRO: {e}'

    # Carga manual via ?load=1
    carga_resultado = None
    if request.GET.get('load') == '1' and fixture_existe:
        try:
            if not Empresa.objects.exists():
                with open(fixture_path, encoding='utf-8') as f:
                    all_data = json.load(f)
                priority_data = [o for o in all_data
                                 if o['model'] in ('auth.group', 'core.empresa', 'auth.user', 'core.perfil')]
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                                 delete=False, encoding='utf-8') as tmp:
                    json.dump(priority_data, tmp, ensure_ascii=False)
                    tmp_path = tmp.name
                try:
                    call_command('loaddata', tmp_path, verbosity=0)
                    carga_resultado = f'OK — {len(priority_data)} registros carregados'
                finally:
                    os.unlink(tmp_path)
            else:
                carga_resultado = 'Empresas já existem, carga ignorada'
        except Exception as e:
            carga_resultado = f'ERRO: {e}'

    # Contagem do banco
    try:
        db_empresas = Empresa.objects.count()
        db_usuarios = User.objects.count()
        db_produtos = Produto.objects.count()
        db_projetos = Projeto.objects.count()
        db_ok = True
        db_erro = None
    except Exception as e:
        db_ok = False
        db_erro = str(e)
        db_empresas = db_usuarios = db_produtos = db_projetos = 0

    empresas_lista = []
    if db_ok:
        for e in Empresa.objects.all():
            empresas_lista.append({
                'id': e.id,
                'nome': e.nome_fantasia,
                'logo': str(e.logo) if e.logo else None,
                'is_sistema': e.is_sistema,
            })

    # GCS
    gcs_ok = False
    gcs_erro = None
    if getattr(settings, 'USE_GCS', False):
        try:
            from google.cloud import storage as gcs
            client = gcs.Client()
            bucket = client.bucket(settings.GS_BUCKET_NAME)
            gcs_ok = bucket.exists()
        except Exception as e:
            gcs_erro = str(e)

    return JsonResponse({
        'banco': {
            'ok': db_ok,
            'erro': db_erro,
            'empresas': db_empresas,
            'usuarios': db_usuarios,
            'produtos': db_produtos,
            'projetos': db_projetos,
        },
        'empresas_cadastradas': empresas_lista,
        'fixture': {
            'path': fixture_path,
            'existe': fixture_existe,
        },
        'carga_manual': carga_resultado,
        'carga_produtos': carga_produtos_resultado,
        'upload_logos': upload_resultado,
        'gcs': {
            'ativo': getattr(settings, 'USE_GCS', False),
            'bucket': getattr(settings, 'GS_BUCKET_NAME', None),
            'bucket_existe': gcs_ok,
            'erro': gcs_erro,
        },
        'debug': settings.DEBUG,
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})
