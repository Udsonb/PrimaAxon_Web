from .models import Empresa, Perfil


def empresa_context(request):
    empresa_logo_url = None
    empresa_nome = None
    user_foto_url = None

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
    except Perfil.DoesNotExist:
        pass
    except Exception:
        pass

    return {
        'empresa_logo_url': empresa_logo_url,
        'empresa_nome': empresa_nome,
        'user_foto_url': user_foto_url,
    }
