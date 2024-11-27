# general_views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import Livro, URLExterna, VideoYouTube
from ..forms import ContatoForm
from ..utils.email_utils import enviar_email_contato

def index(request):
    try:
        context = {
            'livros_destaque': Livro.objects.filter(destaque=True),
            'livros_mais_vendidos': Livro.objects.filter(mais_vendido=True),
            'urls_externas': URLExterna.objects.all(),
            'videos_youtube': VideoYouTube.objects.all(),
        }
        return render(request, 'index.html', context)
    except Exception as e:
        messages.error(request, 'Ocorreu um erro ao carregar a página inicial.')
        return render(request, 'index.html', {})

def sobre(request):
    return render(request, 'sobre.html')

def contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            try:
                contato = form.save()
                emails_enviados = enviar_email_contato(form.cleaned_data)

                if emails_enviados:
                    messages.success(request, 'Mensagem enviada com sucesso! Verifique seu e-mail para confirmação.')
                else:
                    messages.warning(request, 'Sua mensagem foi recebida, mas houve um problema ao enviar o e-mail de confirmação.')

                return redirect('contato')
            except Exception as e:
                messages.error(request, 'Ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.')
    else:
        form = ContatoForm()

    return render(request, 'contato.html', {'form': form})

def politica_privacidade(request):
    return render(request, 'politica_privacidade.html')

def termos_uso(request):
    return render(request, 'termos_uso.html')