from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# ---------------------------
# Gerenciador de Usuários
# ---------------------------
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

# ---------------------------
# Modelo de Usuário
# ---------------------------
class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPO_USUARIO = [
        ('gestao', 'Gestão Condominial'),
        ('contabilidade', 'Contabilidade'),
    ]

    nome = models.CharField(max_length=150, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO, default='gestao')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'nome'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

# ---------------------------
# Condominio
# ---------------------------
class Condominio(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    localizacao = models.CharField(max_length=255)
    horario_atendimento = models.CharField(max_length=100, blank=True, null=True)
    contato = models.CharField(max_length=150, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

# ---------------------------
# Itens Entregáveis
# ---------------------------
class ItemEntregavel(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class DiaOperacao(models.Model):
    data = models.DateField(unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    concluido = models.BooleanField(default=False)

    def __str__(self):
        return self.data.strftime('%d/%m/%Y')

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
    horario_coleta = models.CharField(max_length=20, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    anexo = models.FileField(upload_to='comprovantes/', blank=True, null=True)
    protocolo = models.BooleanField(default=False)
    malote = models.BooleanField(default=False)
    itens_entregues = models.ManyToManyField(ItemEntregavel, blank=True)

    def __str__(self):
        return f"{self.tipo.capitalize()} - {self.condominio.nome} ({self.dia.data.strftime('%d/%m/%Y')})"


class EmpresaContabil(models.Model):
    nome = models.CharField(max_length=150)
    endereco = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class DiaContabil(models.Model):
    data = models.DateField()
    empresa = models.ForeignKey(EmpresaContabil, on_delete=models.CASCADE, null=True)
    concluido = models.BooleanField(default=False)  
    criado_em = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('data', 'empresa')

    def __str__(self):
        return f"{self.empresa.nome} - {self.data.strftime('%d/%m/%Y')}"


class OperacaoContabil(models.Model):
     
    TIPO_CHOICES = [
        ('entrega', 'Entrega'),
        ('retirada', 'Retirada'),
        ('entrega e retirada', 'Entrega e Retirada'),
    ]
    diaContabil = models.ForeignKey(DiaContabil, on_delete=models.CASCADE, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    solicitante = models.CharField(max_length=100)
    documento = models.CharField(max_length=100)
    protocolo = models.BooleanField(default=False)
    malote = models.BooleanField(default=False)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    nome = models.CharField(max_length=100)
    empresa = models.ForeignKey(EmpresaContabil, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.documento} - R${self.valor} - {self.diaContabil}"
