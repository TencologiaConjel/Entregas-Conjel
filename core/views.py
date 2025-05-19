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