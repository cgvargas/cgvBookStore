# profile_views.py
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from core.models import EstanteLivro


@login_required
def profile(request):
    # Obter parâmetros de página da URL
    page_favoritos = request.GET.get('page_fav')
    page_lendo = request.GET.get('page_lendo')
    page_vou_ler = request.GET.get('page_vou_ler')
    page_lidos = request.GET.get('page_lidos')

    # Buscar livros ordenados por data de adição
    favoritos = EstanteLivro.objects.filter(usuario=request.user, tipo='favorito').order_by('-data_adicao')
    lendo = EstanteLivro.objects.filter(usuario=request.user, tipo='lendo').order_by('-data_adicao')
    vou_ler = EstanteLivro.objects.filter(usuario=request.user, tipo='vou_ler').order_by('-data_adicao')
    lidos = EstanteLivro.objects.filter(usuario=request.user, tipo='lido').order_by('-data_adicao')

    # Configurar paginação (8 livros por página)
    paginator_favoritos = Paginator(favoritos, 8)
    paginator_lendo = Paginator(lendo, 8)
    paginator_vou_ler = Paginator(vou_ler, 8)
    paginator_lidos = Paginator(lidos, 8)

    try:
        favoritos_paginados = paginator_favoritos.page(page_favoritos)
        lendo_paginados = paginator_lendo.page(page_lendo)
        vou_ler_paginados = paginator_vou_ler.page(page_vou_ler)
        lidos_paginados = paginator_lidos.page(page_lidos)
    except PageNotAnInteger:
        favoritos_paginados = paginator_favoritos.page(1)
        lendo_paginados = paginator_lendo.page(1)
        vou_ler_paginados = paginator_vou_ler.page(1)
        lidos_paginados = paginator_lidos.page(1)
    except EmptyPage:
        favoritos_paginados = paginator_favoritos.page(paginator_favoritos.num_pages)
        lendo_paginados = paginator_lendo.page(paginator_lendo.num_pages)
        vou_ler_paginados = paginator_vou_ler.page(paginator_vou_ler.num_pages)
        lidos_paginados = paginator_lidos.page(paginator_lidos.num_pages)

    context = {
        'favoritos': favoritos_paginados,
        'lendo': lendo_paginados,
        'vou_ler': vou_ler_paginados,
        'lidos': lidos_paginados,
        'total_livros': favoritos.count() + lendo.count() + vou_ler.count() + lidos.count()
    }

    return render(request, 'perfil.html', context)