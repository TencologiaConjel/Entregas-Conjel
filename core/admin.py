from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Condominio, ItemEntregavel, EmpresaContabil, EnderecoCondominio, ItemEntregue
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class UsuarioCreationForm(forms.ModelForm):
    """Formulário para criação de novos usuários"""
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmação de Senha', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ('nome', 'tipo')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas não coincidem")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UsuarioChangeForm(forms.ModelForm):
    """Formulário para atualização de usuários"""
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Usuario
        fields = ('nome', 'tipo', 'password', 'is_active', 'is_staff', 'is_superuser')


class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm
    model = Usuario
    list_display = ('nome', 'tipo', 'is_staff', 'is_superuser')
    list_filter = ('tipo', 'is_staff', 'is_superuser')
    
    fieldsets = (
        (None, {'fields': ('nome', 'tipo', 'password')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nome', 'tipo', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ('nome',)
    ordering = ('nome',)

@admin.register(Condominio)
class CondominioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'localizacao', 'contato', 'telefone', 'horario_atendimento', 'data_cadastro')
    search_fields = ('nome', 'localizacao', 'contato')

@admin.register(ItemEntregavel)
class ItemEntregavelAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome']
    search_fields = ['nome']

admin.site.register(Usuario, UsuarioAdmin)

@admin.register(EmpresaContabil)
class EmpresaContabilAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco')
    search_fields = ('nome',)

@admin.register(EnderecoCondominio)
class EnderecoCondominioAdmin(admin.ModelAdmin):
    list_display = ('condominio', 'endereco')
    search_fields = ('condominio__nome', 'endereco')

@admin.register(ItemEntregue)  
class ItemRecebidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)
