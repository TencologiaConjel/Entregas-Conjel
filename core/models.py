from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UsuarioManager(BaseUserManager):
    def create_user(self, nome, password=None, **extra_fields):
        if not nome:
            raise ValueError('O nome é obrigatório')
        user = self.model(nome=nome, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nome, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(nome, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    nome = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'nome'
    REQUIRED_FIELDS = [] 

    def __str__(self):
        return self.nome


class Condominio(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    localizacao = models.CharField(max_length=255)
    horario_atendimento = models.CharField(max_length=100, blank=True, null=True)
    contato = models.CharField(max_length=150, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
class DiaOperacao(models.Model):
    data = models.DateField(unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    concluido = models.BooleanField(default=False)

    def __str__(self):
        return self.data.strftime('%d/%m/%Y')
    
class ItemEntregavel(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Operacao(models.Model):
    TIPO_CHOICES = [
        ('coleta', 'Coleta'),
        ('retirada', 'Retirada'),
        ('coleta e retirada', 'Coleta e Retirada'),
    ]

    dia = models.ForeignKey(DiaOperacao, on_delete=models.CASCADE, related_name='operacoes')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    condominio = models.ForeignKey(Condominio, on_delete=models.CASCADE)
    responsavel = models.CharField(max_length=100)
    destinatario = models.CharField(max_length=100, blank=True, null=True)
    horario_coleta = models.CharField(max_length = 20, blank =True, null = True)
    observacoes = models.TextField(blank=True, null=True)
    anexo = models.FileField(upload_to='comprovantes/', blank=True, null=True)
    protocolo = models.BooleanField(default=False)
    malote = models.BooleanField(default=False)
    itens_entregues = models.ManyToManyField(ItemEntregavel, blank=True)

    def __str__(self):
        return f"{self.tipo.capitalize()} - {self.condominio.nome} ({self.data_hora.strftime('%d/%m/%Y %H:%M')})"


