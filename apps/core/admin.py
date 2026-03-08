from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Status,
    StageType,
    MachineModel,
    Workshop,
    Machine,
    Detail,
    Stage,
    MachineAssignment
)


# ============================================================
# БАЗОВЫЙ ADMIN
# ============================================================

class BaseAdmin(admin.ModelAdmin):
    """
    Базовый класс админки.

    Добавляет:

    - даты
    - soft delete
    """

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_deleted",
    )

    list_display = (
        "__str__",
        "created_at",
        "is_deleted"
    )

    search_fields = (
        "id",
    )


# ============================================================
# STATUS ADMIN
# ============================================================

@admin.register(Status)
class StatusAdmin(BaseAdmin):

    list_display = (
        "name",
        "description",
        "created_at",
        "is_deleted"
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "name",
    )


# ============================================================
# STAGE TYPE ADMIN
# ============================================================

@admin.register(StageType)
class StageTypeAdmin(BaseAdmin):

    list_display = (
        "name",
        "description",
        "created_at"
    )

    search_fields = (
        "name",
        "description"
    )


# ============================================================
# MACHINE MODEL ADMIN
# ============================================================

@admin.register(MachineModel)
class MachineModelAdmin(BaseAdmin):

    list_display = (
        "name",
        "manufacturer",
        "created_at"
    )

    search_fields = (
        "name",
        "manufacturer"
    )


# ============================================================
# WORKSHOP ADMIN
# ============================================================

@admin.register(Workshop)
class WorkshopAdmin(BaseAdmin):

    list_display = (
        "code",
        "name",
        "created_at"
    )

    search_fields = (
        "name",
        "code"
    )


# ============================================================
# STAGE INLINE
# ============================================================

class StageInline(admin.TabularInline):
    """
    Inline этапов внутри детали.
    """

    model = Stage

    extra = 0

    autocomplete_fields = (
        "machine",
        "stage_type"
    )

    fields = (
        "order_num",
        "stage_type",
        "machine",
        "is_completed",
        "completion_date",
    )

    ordering = (
        "order_num",
    )


# ============================================================
# ASSIGNMENT INLINE
# ============================================================

class AssignmentInline(admin.TabularInline):

    model = MachineAssignment

    extra = 0

    autocomplete_fields = (
        "machine",
    )

    fields = (

        "machine",

        "planned_start",

        "planned_end",

        "actual_start",

        "actual_end",

    )


# ============================================================
# MACHINE ADMIN
# ============================================================

@admin.register(Machine)
class MachineAdmin(BaseAdmin):

    list_display = (

        "inventory_number",

        "model",

        "workshop",

        "status",

        "load_indicator",

        "commissioning_date",

    )

    search_fields = (

        "inventory_number",

        "model__name",

        "workshop__name",

    )

    list_filter = (

        "status",

        "model",

        "workshop",

    )

    autocomplete_fields = (

        "model",

        "workshop",

        "status",

    )

    fieldsets = (

        ("Основное",

            {

                "fields": (

                    "inventory_number",

                    "model",

                    "workshop",

                    "status",

                )

            }
        ),

        ("Загрузка",

            {

                "fields": (

                    "load_percent",

                )

            }
        ),

        ("Обслуживание",

            {

                "fields": (

                    "commissioning_date",

                    "last_maintenance_date",

                )

            }
        ),

        ("Служебные поля",

            {

                "fields": (

                    "created_at",

                    "updated_at",

                    "is_deleted"

                )

            }
        )

    )

    # ===================================
    # Цвет загрузки
    # ===================================

    def load_indicator(self, obj):

        color = "green"

        if obj.load_percent > 80:
            color = "red"

        elif obj.load_percent > 50:
            color = "orange"

        return format_html(

            '<b style="color:{};">{} %</b>',

            color,

            obj.load_percent

        )

    load_indicator.short_description = "Загрузка"



# ============================================================
# DETAIL ADMIN
# ============================================================

@admin.register(Detail)
class DetailAdmin(BaseAdmin):

    inlines = [
        StageInline,
        AssignmentInline,
    ]

    list_display = (
        "article",
        "name",
        "drawing_number",
        "status",
        "completion_indicator",
        "planned_completion_date",
    )

    search_fields = (
        "article",
        "name",
        "drawing_number"
    )

    list_filter = (
        "status",
        "planned_completion_date",
    )

    autocomplete_fields = (
        "status",
    )

    fieldsets = (
        ("Основная информация",
            {
                "fields": (
                    "article",
                    "name",
                    "drawing_number",
                    "status",
                )
            }
        ),

        ("Готовность",
            {
                "fields": (
                    "completion_percent",
                    "planned_completion_date",
                )
            }
        ),

        ("Описание",
            {
                "fields": (
                    "description",
                )
            }
        ),

        ("Служебные поля",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "is_deleted"
                )
            }
        )
    )

    readonly_fields = (
        "completion_percent",
        "created_at",
        "updated_at",
    )

    # ===================================
    # Цвет готовности
    # ===================================

    def completion_indicator(self, obj):

        color = "red"

        if obj.completion_percent > 80:
            color = "green"

        elif obj.completion_percent > 40:
            color = "orange"

        return format_html(

            '<b style="color:{};">{} %</b>',

            color,

            obj.completion_percent

        )

    completion_indicator.short_description = "Готовность"



# ============================================================
# STAGE ADMIN
# ============================================================

@admin.register(Stage)
class StageAdmin(BaseAdmin):

    list_display = (
        "detail",
        "order_num",
        "stage_type",
        "machine",
        "is_completed",
        "completion_date",
    )

    search_fields = (
        "detail__article",
        "machine__inventory_number",
    )

    list_filter = (
        "is_completed",
        "stage_type",
        "machine",
    )

    autocomplete_fields = (
        "detail",
        "machine",
        "stage_type",
    )



# ============================================================
# ASSIGNMENT ADMIN
# ============================================================

@admin.register(MachineAssignment)
class MachineAssignmentAdmin(BaseAdmin):

    list_display = (
        "machine",
        "detail",
        "planned_start",
        "planned_end",
        "actual_start",
        "actual_end",
    )

    search_fields = (
        "machine__inventory_number",
        "detail__article",
    )

    list_filter = (
        "machine",
    )

    autocomplete_fields = (
        "machine",
        "detail",
    )


from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin.views.main import ChangeList
from .models import LogEntry


class ReadOnlyAdminMixin:
    """Миксин для запрета редактирования, добавления и удаления"""
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class LogEntryChangeList(ChangeList):
    """Кастомный ChangeList для отображения полей только для чтения"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(LogEntry)
class LogEntryAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """
    Административный интерфейс для журнала действий.
    Только для чтения.
    """
    
    list_display = [
        'created_at_colored',
        'user_info',
        'action_colored',
        'entity_link',
        'description_short',
        'ip_address',
    ]
    
    list_filter = [
        'action_type',
        'entity_type',
        'user',
        ('created_at', admin.DateFieldListFilter),
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'description',
        'entity_type',
        'entity_id',
        'ip_address',
    ]
    
    readonly_fields = [
        'user',
        'action_type',
        'entity_type',
        'entity_id',
        'description',
        'changes_json',
        'ip_address',
        'created_at',
        'updated_at',
        'get_entity_link',
        'get_changes_preview',
    ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'user',
                'action_type',
                'created_at',
            )
        }),
        ('Объект', {
            'fields': (
                'entity_type',
                'entity_id',
                'get_entity_link',
            )
        }),
        ('Детали действия', {
            'fields': (
                'description',
                'get_changes_preview',
            )
        }),
        ('Техническая информация', {
            'classes': ('collapse',),
            'fields': (
                'ip_address',
                'updated_at',
                'changes_json',
            )
        }),
    )
    
    date_hierarchy = 'created_at'
    
    list_per_page = 50
    
    actions = None  # Отключаем все действия
    
    def get_changelist(self, request, **kwargs):
        return LogEntryChangeList
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def created_at_colored(self, obj):
        """
        Цветовое отображение даты в зависимости от давности
        """
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        if obj.created_at > now - timedelta(hours=1):
            color = '#28a745'  # свежие - зелёные
        elif obj.created_at > now - timedelta(days=1):
            color = '#ffc107'  # сегодняшние - жёлтые
        elif obj.created_at > now - timedelta(days=7):
            color = '#17a2b8'  # недельной давности - голубые
        else:
            color = '#6c757d'  # старые - серые
        
        return format_html(
            '<span style="color: {}; font-weight: 500;">{}</span><br>'
            '<small style="color: #999;">{}</small>',
            color,
            obj.created_at.strftime('%d.%m.%Y'),
            obj.created_at.strftime('%H:%M:%S')
        )
    created_at_colored.short_description = 'Дата и время'
    created_at_colored.admin_order_field = 'created_at'
    
    def user_info(self, obj):
        """
        Информация о пользователе с аватаркой
        """
        if not obj.user:
            return format_html(
                '<span style="color: #999;"><i>Система</i></span>'
            )
        
        user_url = reverse('admin:auth_user_change', args=[obj.user.id])
        initials = obj.user.username[:2].upper() if obj.user.username else '??'
        
        return format_html(
            '<div style="display: flex; align-items: center;">'
            '<div style="width: 32px; height: 32px; background: var(--primary-color); '
            'border-radius: 50%; display: flex; align-items: center; justify-content: center; '
            'margin-right: 8px; color: white; font-weight: 600; font-size: 12px;">{}</div>'
            '<div><a href="{}" style="font-weight: 500;">{}</a><br>'
            '<small style="color: #666;">{}</small></div>'
            '</div>',
            initials,
            user_url,
            obj.user.get_full_name() or obj.user.username,
            obj.user.email or ''
        )
    user_info.short_description = 'Пользователь'
    user_info.admin_order_field = 'user__username'
    
    def action_colored(self, obj):
        """
        Цветовое отображение типа действия
        """
        colors = {
            'CREATE': {'bg': '#d4edda', 'text': '#155724', 'icon': 'bi-plus-circle-fill'},
            'UPDATE': {'bg': '#cce5ff', 'text': '#004085', 'icon': 'bi-pencil-fill'},
            'DELETE': {'bg': '#f8d7da', 'text': '#721c24', 'icon': 'bi-trash-fill'},
            'STATUS_CHANGE': {'bg': '#fff3cd', 'text': '#856404', 'icon': 'bi-arrow-repeat'},
            'STAGE_COMPLETE': {'bg': '#d1e7dd', 'text': '#0f5132', 'icon': 'bi-check-circle-fill'},
            'RECALCULATE': {'bg': '#cff4fc', 'text': '#055160', 'icon': 'bi-calculator-fill'},
            'ASSIGNMENT': {'bg': '#e2d5f1', 'text': '#4a2e7a', 'icon': 'bi-cpu-fill'},
        }
        
        color = colors.get(obj.action_type, {'bg': '#e9ecef', 'text': '#495057', 'icon': 'bi-question-circle'})
        
        return format_html(
            '<span style="background: {}; color: {}; padding: 4px 8px; border-radius: 4px; '
            'font-size: 12px; font-weight: 500; display: inline-flex; align-items: center; gap: 4px;">'
            '<i class="bi {}"></i> {}</span>',
            color['bg'],
            color['text'],
            color['icon'],
            obj.get_action_type_display()
        )
    action_colored.short_description = 'Действие'
    action_colored.admin_order_field = 'action_type'
    
    def entity_link(self, obj):
        """
        Ссылка на изменённый объект
        """
        # Пытаемся получить ссылку на объект
        try:
            # Проверяем, есть ли у объекта админка
            app_label = 'core'  
            model_name = obj.entity_type.lower()
            
            # Проверяем, существует ли модель с таким именем
            from django.apps import apps
            try:
                model = apps.get_model(app_label, model_name)
                if model:
                    url = reverse(f'admin:{app_label}_{model_name}_change', args=[obj.entity_id])
                    return format_html(
                        '<a href="{}" style="font-weight: 500;">{} #{}</a><br>'
                        '<small style="color: #666;">{}</small>',
                        url,
                        obj.entity_type,
                        obj.entity_id,
                        obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
                    )
            except:
                pass
        except:
            pass
        
        # Если не удалось получить ссылку, показываем просто текст
        return format_html(
            '<strong>{} #{}</strong><br><small style="color: #666;">{}</small>',
            obj.entity_type,
            obj.entity_id,
            obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        )
    entity_link.short_description = 'Объект'
    
    def description_short(self, obj):
        """
        Краткое описание
        """
        if len(obj.description) > 60:
            return format_html(
                '<span title="{}">{}</span>',
                obj.description,
                obj.description[:60] + '...'
            )
        return obj.description
    description_short.short_description = 'Описание'
    
    def get_entity_link(self, obj):
        """
        Ссылка на объект для детального просмотра
        """
        return self.entity_link(obj)
    get_entity_link.short_description = 'Объект'
    
    def get_changes_preview(self, obj):
        """
        Предпросмотр изменений в JSON формате
        """
        if not obj.changes_json:
            return '-'
        
        # Форматируем JSON для красивого отображения
        import json
        formatted_json = json.dumps(obj.changes_json, indent=2, ensure_ascii=False)
        
        return format_html(
            '<pre style="background: #f8f9fa; padding: 10px; border-radius: 5px; '
            'max-height: 300px; overflow: auto; font-size: 11px;">{}</pre>',
            formatted_json
        )
    get_changes_preview.short_description = 'Детали изменений'
    
    # Дополнительные настройки для улучшения просмотра
    
    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css',)
        }


# Виджет для фильтрации по датам
class DateRangeFilter(admin.SimpleListFilter):
    """Кастомный фильтр по диапазону дат"""
    
    title = 'Период'
    parameter_name = 'date_range'
    
    def lookups(self, request, model_admin):
        return [
            ('today', 'Сегодня'),
            ('yesterday', 'Вчера'),
            ('week', 'Последние 7 дней'),
            ('month', 'Последние 30 дней'),
            ('quarter', 'Последние 3 месяца'),
        ]
    
    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if self.value() == 'today':
            return queryset.filter(created_at__date=now.date())
        if self.value() == 'yesterday':
            yesterday = now - timedelta(days=1)
            return queryset.filter(created_at__date=yesterday.date())
        if self.value() == 'week':
            return queryset.filter(created_at__gte=now - timedelta(days=7))
        if self.value() == 'month':
            return queryset.filter(created_at__gte=now - timedelta(days=30))
        if self.value() == 'quarter':
            return queryset.filter(created_at__gte=now - timedelta(days=90))
        return queryset