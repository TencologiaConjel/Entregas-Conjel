from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=username, password=senha)

        if user:
            login(request, user)
            return redirect('inicio_analista')  
        else:
            return render(request, 'financeiro/login.html', {
                'erro': 'Usuário ou senha inválidos',
                'hide_navbar': True
            })

    return render(request, 'login.html', {
        'hide_navbar': True
    })

from django.http import HttpResponse
from django.contrib.auth import get_user_model

def criar_superusuario(request):
    Usuario = get_user_model()

    if Usuario.objects.filter(is_superuser=True).exists():
        return HttpResponse("Superusuário já existe.")

    Usuario.objects.create_superuser(
        nome='admin',
        password='admin1234',
        is_active=True,
        is_staff=True
    )
    return HttpResponse("Superusuário criado com sucesso!")
