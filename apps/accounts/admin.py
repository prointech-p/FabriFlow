from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group

from .models import User


# Отменяем регистрацию стандартных моделей

# Сначала снимаем регистрацию стандартного User, если он уже зарегистрирован
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass  # Игнорируем ошибку, если модель ещё не зарегистрирована


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Отображение в списке
    list_display = [
        'username', 
        'email', 
        'position', 
        'phone', 
        'is_staff', 
        'is_active',
        'date_joined'
    ]
    
    list_filter = [
        'is_staff', 
        'is_active', 
        'date_joined',
        'position'
    ]
    
    search_fields = [
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'position',
        'phone'
    ]
    
    ordering = ['-date_joined']
    
    # Группировка полей в форме редактирования
    fieldsets = UserAdmin.fieldsets + (
        ('Профиль компании', {
            'fields': ('position', 'phone')
        }),
    )
    
    # Поля при создании пользователя
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Профиль компании', {
            'fields': ('position', 'phone', 'email')  # email добавлен для удобства
        }),
    )
      



# Регистрируем Group обратно
@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    pass
