from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime

from .models import Operacao, DiaOperacao, Condominio, ItemEntregavel, DiaContabil, EmpresaContabil,OperacaoContabil


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=username, password=senha)

        if user is not None:
            login(request, user)

            if user.tipo == 'gestao':
                return redirect('demanda')  
            elif user.tipo == 'contabilidade':
                return redirect('painel_contabilidade')  
            else:
                return redirect('admin:index')  

        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'login.html', {'hide_navbar': True})

def logout_view(request):
    logout(request)
    messages.success(request, 'Você saiu da sua conta com sucesso.')
    return redirect('login')


def demanda(request):
    if request.method == 'POST':
        if 'concluir_dia_id' in request.POST:
        
            dia_id = request.POST.get('concluir_dia_id')
            dia = get_object_or_404(DiaOperacao, id=dia_id)
            dia.concluido = True
            dia.save()
            messages.success(request, f"Dia {dia.data.strftime('%d/%m/%Y')} marcado como concluído.")
            return redirect('demanda')
        else:
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

    todos_dias = DiaOperacao.objects.all().order_by('-data')
    dias_abertos = todos_dias.filter(concluido=False)
    dias_concluidos = todos_dias.filter(concluido=True)

    for dia in dias_abertos:
        dia.operacao_principal = dia.operacoes.first()

    return render(request, 'demanda.html', {
        'dias': dias_abertos,
        'concluidos': dias_concluidos,
    })



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
    operacoes_list = Operacao.objects.prefetch_related('itens_entregues') \
                                     .select_related('dia', 'condominio') \
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
    if request.method == 'POST':
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

        messages.success(request, f"Nova operação copiada com base na operação {operacao_id}.")
        return redirect('detalhar_dia', dia_id=operacao_original.dia.id)
    else:
        return redirect('entregas_finalizadas')

def visualizar_dia(request, dia_id):
    dia = get_object_or_404(DiaOperacao, id=dia_id)
    operacoes = Operacao.objects.filter(dia=dia).order_by('horario_coleta')
    condominios = Condominio.objects.all()
    itens = ItemEntregavel.objects.all()

    if request.method == 'POST':
        for operacao in operacoes:
            operacao_id = str(operacao.id)
            observacoes = request.POST.get(f'observacoes_{operacao_id}', '').strip()
            protocolo = request.POST.get(f'protocolo_{operacao_id}') == 'on'
            malote = request.POST.get(f'malote_{operacao_id}') == 'on'
            itens_ids = request.POST.getlist(f'itens_{operacao_id}')

            operacao.observacoes = observacoes
            operacao.protocolo = protocolo
            operacao.malote = malote
            operacao.itens_entregues.set(itens_ids)
            operacao.save()

        messages.success(request, 'Informações atualizadas com sucesso.')
        return redirect('visualizar_dia', dia_id=dia_id)

    return render(request, 'visualizar_dia.html', {
        'dia': dia,
        'operacoes': operacoes,
        'condominios': condominios,
        'itens': itens
    })

def painel_contabilidade(request):
    usuario = request.user

    if request.method == 'POST':
        if 'concluir_dia_id' in request.POST:
            dia_id = request.POST.get('concluir_dia_id')
            dia = get_object_or_404(DiaContabil, id=dia_id)
            dia.concluido = True
            dia.save()
            messages.success(request, f"Dia {dia.data.strftime('%d/%m/%Y')} marcado como concluído.")
            return redirect('painel_contabilidade')

        elif 'data' in request.POST:
            data_str = request.POST.get('data')
            try:
                nova_data = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Data inválida.")
                return redirect('painel_contabilidade')

            if DiaContabil.objects.filter(data=nova_data).exists():
                messages.warning(request, "Esse dia já existe.")
            else:
                DiaContabil.objects.create(data=nova_data, empresa=None)
                messages.success(request, "Dia cadastrado com sucesso.")

            return redirect('painel_contabilidade')

    todas_empresas = EmpresaContabil.objects.all()
    todos_dias = DiaContabil.objects.select_related('empresa').order_by('-data')

    dias_abertos = todos_dias.filter(concluido=False)
    dias_concluidos = todos_dias.filter(concluido=True).distinct()

    return render(request, 'painel_contabil.html', {
        'empresas': todas_empresas,
        'dias': dias_abertos,
        'dias_concluidos': dias_concluidos,
    })

def detalhar_dia_contabil(request, dia_id):
    if request.user.tipo != 'contabilidade':
        return redirect('demanda')

    dia = get_object_or_404(DiaContabil, id=dia_id)
    operacoes = OperacaoContabil.objects.filter(diaContabil=dia)
    empresas = EmpresaContabil.objects.all()

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        solicitante = request.POST.get('solicitante')
        documento = request.POST.get('documento') 
        protocolo = request.POST.get('protocolo') == 'on'
        malote = request.POST.get('malote') == 'on'
        valor = request.POST.get('valor')
        empresa_id = request.POST.get('empresa_id')

        if not empresa_id:
            messages.error(request, "Empresa contábil não foi selecionada.")
            return redirect('detalhar_dia_contabil', dia_id=dia.id)

        empresa = get_object_or_404(EmpresaContabil, id=empresa_id)

        OperacaoContabil.objects.create(
            diaContabil=dia,
            tipo=tipo,
            solicitante=solicitante,
            documento=documento,
            protocolo = protocolo,
            malote = malote,
            valor=valor,
            empresa = empresa
        )

        messages.success(request, "Operação contábil cadastrada com sucesso.")
        return redirect('detalhar_dia_contabil', dia_id=dia.id)

    return render(request, 'detalhes_dia_contabil.html', {
        'dia': dia,
        'operacoes': operacoes,
        'empresas': empresas,
    })


from django.contrib.auth import get_user_model
User = get_user_model()

def criar_superusuario_auto(request):
    if User.objects.filter(is_superuser=True).exists():
        messages.info(request, "Já existe um superusuário cadastrado.")
        return redirect('login')

    if not User.objects.filter(nome='admin').exists():
        User.objects.create_superuser(
            nome='admin',
            password='admin1234',
            tipo='gestao'
        )
        messages.success(request, "Superusuário 'admin' criado com sucesso! (senha: admin1234)")
    else:
        messages.warning(request, "Usuário 'admin' já existe.")

    return redirect('login')


def visualizar_dia_contabil(request, dia_id):
    if request.user.tipo != 'contabilidade':
        messages.error(request, "Acesso negado.")
        return redirect('painel_contabilidade')

    dia = get_object_or_404(DiaContabil, id=dia_id)
    operacoes = OperacaoContabil.objects.filter(diaContabil=dia)
    empresas = EmpresaContabil.objects.all()

    if request.method == 'POST':
        for operacao in operacoes:
            op_id = str(operacao.id)
            protocolo = request.POST.get(f'protocolo_{op_id}') == 'on'
            malote = request.POST.get(f'malote_{op_id}') == 'on'
            observacoes = request.POST.get(f'observacoes_{op_id}', '').strip()

            operacao.protocolo = protocolo
            operacao.malote = malote
            operacao.observacoes = observacoes
            operacao.save()

        messages.success(request, 'Informações atualizadas com sucesso.')
        return redirect('visualizar_dia_contabil', dia_id=dia_id)

    return render(request, 'visualizar_dia_contabil.html', {
        'dia': dia,
        'operacoes': operacoes,
        'empresas': empresas,
    })