# core/presentation/admin/user_admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from core.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'nome_completo', 'exibir_imagem', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'data_registro', 'groups']
    search_fields = ['username', 'email', 'nome_completo']
    ordering = ['-data_registro']

    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('nome_completo', 'profile_image', 'data_registro'),
            'classes': ('wide',)
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('nome_completo', 'email', 'profile_image'),
            'classes': ('wide',)
        }),
    )

    readonly_fields = ['data_registro']

    def exibir_imagem(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%;" />',
                obj.profile_image.url
            )
        return "Sem foto"

    exibir_imagem.short_description = 'Foto'