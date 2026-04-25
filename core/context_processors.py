from .models import Empresa, Perfil


def empresa_context(request):
    empresa_logo_url = None
    empresa_nome = None
    user_foto_url = None
    user_cargo = 'analista'
    user_cargo_display = 'Analista'

    try:
        empresa_id = request.session.get('empresa_id')
        if empresa_id:
            empresa = Empresa.objects.get(id=empresa_id)
            empresa_nome = empresa.nome_fantasia
            if empresa.logo:
                empresa_logo_url = empresa.logo.url
    except Exception:
        pass

    try:
        if request.user.is_authenticated:
            perfil = Perfil.objects.get(user=request.user)
            if perfil.foto:
                user_foto_url = perfil.foto.url
            user_cargo = perfil.cargo or 'analista'
            user_cargo_display = perfil.get_cargo_display()
    except Perfil.DoesNotExist:
        pass
    except Exception:
        pass

    # Grupos pré-calculados para uso direto nos templates
    is_diretoria  = user_cargo in {'diretor_geral', 'diretor_setor'}
    is_gerencia   = user_cargo in {'gerente_pre_vendas', 'supervisor'}
    is_compras    = user_cargo in {'gerente_compras', 'comprador', 'orcamentista'}
    is_analista   = user_cargo == 'analista'
    is_comercial  = user_cargo in {'gerente_comercial', 'executivo'}
    can_admin     = is_diretoria  # acesso a gestão de usuários/empresas/programa

    return {
        'empresa_logo_url':   empresa_logo_url,
        'empresa_nome':       empresa_nome,
        'user_foto_url':      user_foto_url,
        'user_cargo':         user_cargo,
        'user_cargo_display': user_cargo_display,
        'is_diretoria':       is_diretoria,
        'is_gerencia':        is_gerencia,
        'is_compras':         is_compras,
        'is_analista':        is_analista,
        'is_comercial':       is_comercial,
        'can_admin':          can_admin,
    }
