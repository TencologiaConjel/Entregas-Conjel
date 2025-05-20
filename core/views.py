from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Operacao, DiaOperacao, Condominio, ItemEntregavel
from datetime import datetime
from django.db.models.functions import TruncDate
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth import logout


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=username, password=senha)

        if user is not None:
            login(request, user)
            return redirect('demanda')  
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'login.html', {'hide_navbar': True})

def demanda(request):
    if request.method == 'POST':
        data_str = request.POST.get('data')

        try:
            nova_data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Data inválida.")
            return redirect('demanda')

        if DiaOperacao.objects.filter(data=nova_data).exists():
            messages.warning(request, "Esse dia já existe.")
        else:
            DiaOperacao.objects.create(data=nova_data)
            messages.success(request, "Dia cadastrado com sucesso.")

        return redirect('demanda')

    dias = DiaOperacao.objects.all().order_by('-data')

    for dia in dias:
     dia.operacao_principal = dia.operacoes.first()
    return render(request, 'demanda.html', {'dias': dias})

def detalhar_dia(request, dia_id):
    dia = get_object_or_404(DiaOperacao, id=dia_id)
    operacoes = Operacao.objects.filter(dia=dia).order_by('horario_coleta')
    condominios = Condominio.objects.all()

    if request.method == 'POST':
        condominio_id = request.POST.get('condominio_id')
        tipo = request.POST.get('tipo')
        responsavel = request.POST.get('responsavel')
        protocolo = request.POST.get('protocolo') == 'on'
        malote = request.POST.get('malote') == 'on'

        try:
            condominio = Condominio.objects.get(id=condominio_id)
            destinatario = request.POST.get('destinatario') or condominio.localizacao
        except Condominio.DoesNotExist:
            messages.error(request, "Condomínio inválido.")
            return redirect('detalhar_dia', dia_id=dia.id)

        Operacao.objects.create(
            dia=dia,
            condominio=condominio,
            tipo=tipo,
            responsavel=responsavel,
            destinatario=destinatario,
            protocolo=protocolo,
            malote=malote,
        )

        messages.success(request, "Operação cadastrada com sucesso.")
        return redirect('detalhar_dia', dia_id=dia.id)

    return render(request, 'detalhes_dia.html', {
        'dia': dia,
        'operacoes': operacoes,
        'condominios': condominios
    })

def editar_operacao(request, operacao_id):
    operacao = get_object_or_404(Operacao, id=operacao_id)
    itens = ItemEntregavel.objects.all()

    if request.method == 'POST':
        observacoes = request.POST.get('observacoes')
        itens_ids = request.POST.getlist('itens_entregues')

        operacao.observacoes = observacoes
        operacao.itens_entregues.set(itens_ids)
        operacao.save()

        return redirect('entregas_finalizadas')  

    return render(request, 'editar_operacao.html', {
        'operacao': operacao,
        'itens': itens,
    })

def entregas_finalizadas(request):
    operacoes_list = Operacao.objects.prefetch_related('itens_entregues')\
                                     .select_related('dia', 'condominio')\
                                     .order_by('-dia__data', '-id')

    paginator = Paginator(operacoes_list, 10) 
    page_number = request.GET.get('page')
    operacoes = paginator.get_page(page_number)

    condominios = Condominio.objects.all()

    return render(request, 'entregas_finalizadas.html', {
    'operacoes': operacoes,
    'condominios': condominios
})


def copiar_operacao(request, operacao_id):
    operacao_original = get_object_or_404(Operacao, id=operacao_id)

    nova_operacao = Operacao.objects.create(
        dia=operacao_original.dia,
        condominio=operacao_original.condominio,
        tipo=operacao_original.tipo,
        responsavel=operacao_original.responsavel,
        destinatario=operacao_original.destinatario,
        protocolo=operacao_original.protocolo,
        malote=operacao_original.malote,
        observacoes=operacao_original.observacoes
    )

    nova_operacao.itens_entregues.set(operacao_original.itens_entregues.all())
    nova_operacao.save()

    messages.success(request, f"Nova operação criada com base na operação {operacao_id}.")
    return redirect('detalhar_dia', dia_id=operacao_original.dia.id)

def logout_view(request):
    logout(request)
    messages.success(request, 'Você saiu da sua conta com sucesso.')
    return redirect('login') 