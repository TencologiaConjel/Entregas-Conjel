from django.urls import path
from . import views


urlpatterns = [
  path('', views.login_view, name='login'),
  path('demanda/', views.demanda, name='demanda'),
  path('demanda/<int:dia_id>/', views.detalhar_dia, name='detalhar_dia'),
  path('historico/editar/<int:operacao_id>/', views.editar_operacao, name='editar_operacao'),
  path('entregas/finalizadas/', views.entregas_finalizadas, name='entregas_finalizadas'),
  path('operacao/copiar/<int:operacao_id>/', views.copiar_operacao, name='copiar_operacao'),
  path('logout', views.logout_view, name='logout'),
  path('visualizar-dia/<int:dia_id>/', views.visualizar_dia, name='visualizar_dia'),

  path('painel-contabilidade/', views.painel_contabilidade, name='painel_contabilidade'),
  path('dia-contabil/<int:dia_id>/', views.detalhar_dia_contabil, name='detalhar_dia_contabil'),

]