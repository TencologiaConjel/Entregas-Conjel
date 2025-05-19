from django.urls import path
from . import views


urlpatterns = [
  path('', views.login_view, name='login'),
  path('demanda/', views.demanda, name='demanda'),
  path('demanda/<int:dia_id>/', views.detalhar_dia, name='detalhar_dia'),
]