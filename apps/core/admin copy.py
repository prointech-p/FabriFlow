# from django.contrib import admin
# from django.utils.html import format_html
# from django.urls import reverse
# from django.db.models import Q, Count
# from .models import Status, StageType, MachineModel, Workshop


# # ============================================================
# # БАЗОВЫЙ КЛАСС ДЛЯ ВСЕХ СПРАВОЧНИКОВ
# # ============================================================

# class BaseDictAdmin(admin.ModelAdmin):
#     """
#     Базовый класс админки для справочников.
#     Содержит общие настройки и методы для всех справочников.
#     """
#     # Поля, доступные только для чтения
#     readonly_fields = ['created_at', 'updated_at', 'get_usage_count']
    
#     # Настройки поиска
#     search_fields = ['name', 'description']
    
#     # Настройки фильтров
#     list_filter = ['is_deleted']
    
#     # Поля для сохранения
#     # save_on_top = True
#     save_as = True
    
#     fieldsets = (
#         ('Основная информация', {
#             'fields': ('name', 'description')
#         }),
#         ('Служебная информация', {
#             'classes': ('collapse',),
#             'fields': ('is_deleted', 'created_at', 'updated_at', 'get_usage_count')
#         }),
#     )
    
#     def get_usage_count(self, obj):
#         """
#         Абстрактный метод, должен быть переопределён в дочерних классах.
#         Показывает количество использований записи.
#         """
#         return "N/A"
#     get_usage_count.short_description = "Использований"
    
#     def delete_queryset(self, request, queryset):
#         """
#         Мягкое удаление вместо физического.
#         """
#         for obj in queryset:
#             obj.is_deleted = True
#             obj.save()


# # ============================================================
# # АДМИНКА ДЛЯ СТАТУСОВ
# # ============================================================

# @admin.register(Status)
# class StatusAdmin(BaseDictAdmin):
#     """
#     Административный интерфейс для справочника статусов.
    
#     Особенности:
#     - Отображение статистики использования статусов
#     - Фильтрация по типу использования
#     - Быстрое редактирование основных полей
#     """
    
#     # Отображаемые поля в списке
#     list_display = [
#         'name',
#         'colored_status',
#         'details_count',
#         'machines_count',
#         'is_deleted',
#         'created_at'
#     ]
    
#     # Поля для редактирования в списке
#     list_editable = ['is_deleted']
    
#     # Поля для фильтрации
#     list_filter = [
#         'is_deleted',
#         ('details', admin.EmptyFieldListFilter),  # Статусы, используемые в деталях
#         ('machines', admin.EmptyFieldListFilter),  # Статусы, используемые в станках
#     ]
    
#     # Поиск по полям
#     search_fields = ['name', 'description']
    
#     # Группировка по дате
#     date_hierarchy = 'created_at'
    
#     # Количество записей на странице
#     list_per_page = 25
    
#     def colored_status(self, obj):
#         """
#         Отображает статус с цветовым оформлением.
#         """
#         colors = {
#             'в работе': '#28a745',      # зелёный
#             'завершено': '#17a2b8',      # голубой
#             'ожидание': '#ffc107',        # жёлтый
#             'неисправен': '#dc3545',      # красный
#             'ремонт': '#fd7e14',          # оранжевый
#             'настройка': '#6c757d',       # серый
#         }
        
#         # Приводим к нижнему регистру для поиска по словарю
#         color = colors.get(obj.name.lower(), '#6c757d')
        
#         return format_html(
#             '<span style="color: {}; font-weight: bold;">⬤</span> {}',
#             color,
#             obj.name
#         )
#     colored_status.short_description = 'Статус'
#     colored_status.admin_order_field = 'name'
    
#     def details_count(self, obj):
#         """
#         Количество деталей с этим статусом.
#         """
#         count = obj.details.count()
#         if count > 0:
#             url = reverse('admin:app_detail_changelist') + f'?status__id__exact={obj.id}'
#             return format_html('<a href="{}">{} деталей</a>', url, count)
#         return '-'
#     details_count.short_description = 'Детали'
    
#     def machines_count(self, obj):
#         """
#         Количество станков с этим статусом.
#         """
#         count = obj.machines.count()
#         if count > 0:
#             url = reverse('admin:app_machine_changelist') + f'?status__id__exact={obj.id}'
#             return format_html('<a href="{}">{} станков</a>', url, count)
#         return '-'
#     machines_count.short_description = 'Станки'
    
#     def get_usage_count(self, obj):
#         """
#         Общее количество использований статуса.
#         Переопределение базового метода.
#         """
#         return obj.details.count() + obj.machines.count()
#     get_usage_count.short_description = 'Всего использований'
    
#     fieldsets = (
#         ('Основная информация', {
#             'fields': ('name', 'description')
#         }),
#         ('Статистика использования', {
#             'classes': ('wide',),
#             'fields': ('get_usage_count',),
#             'description': 'Показывает, сколько объектов используют этот статус'
#         }),
#         ('Служебная информация', {
#             'classes': ('collapse',),
#             'fields': ('is_deleted', 'created_at', 'updated_at')
#         }),
#     )


# # ============================================================
# # АДМИНКА ДЛЯ ТИПОВ ЭТАПОВ
# # ============================================================

# @admin.register(StageType)
# class StageTypeAdmin(BaseDictAdmin):
#     """
#     Административный интерфейс для справочника типов этапов.
    
#     Особенности:
#     - Отображение популярности этапов
#     - Предупреждения при удалении часто используемых этапов
#     - Группировка по частоте использования
#     """
    
#     list_display = [
#         'name',
#         'preview_description',
#         'is_deleted'
#     ]
    
#     list_editable = ['is_deleted']
    
#     list_filter = [
#         'is_deleted',
#     ]
    
#     search_fields = ['name', 'description']
    
#     # Действия над выбранными элементами
#     actions = ['mark_as_deleted', 'export_as_csv']
    
#     def preview_description(self, obj):
#         """
#         Превью описания (первые 50 символов).
#         """
#         if obj.description:
#             return obj.description[:50] + ('...' if len(obj.description) > 50 else '')
#         return '-'
#     preview_description.short_description = 'Описание (превью)'
       
#     def mark_as_deleted(self, request, queryset):
#         """
#         Действие: пометить как удалённые.
#         """
#         updated = queryset.update(is_deleted=True)
#         self.message_user(
#             request,
#             f'Помечено как удалённые: {updated} типов этапов'
#         )
#     mark_as_deleted.short_description = 'Пометить как удалённые'
    
# # ============================================================
# # АДМИНКА ДЛЯ МОДЕЛЕЙ СТАНКОВ
# # ============================================================

# @admin.register(MachineModel)
# class MachineModelAdmin(BaseDictAdmin):
#     """
#     Административный интерфейс для справочника моделей станков.
    
#     Особенности:
#     - Отображение количества станков каждой модели
#     - Группировка по производителям
#     - Быстрый фильтр по наличию станков
#     """
    
#     list_display = [
#         'name',
#         'manufacturer',
#         'machines_count',
#         'get_machines_preview',
#         'is_deleted'
#     ]
    
#     list_editable = ['is_deleted']
    
#     list_filter = [
#         'manufacturer',
#         'is_deleted',
#         'machines__workshop',  # Фильтр по цехам, где есть такие станки
#     ]
    
#     search_fields = ['name', 'manufacturer', 'description']
    
#     # Поля для группировки
#     list_display_links = ['name']
    
#     # Поля для редактирования в форме
#     fieldsets = (
#         ('Информация о модели', {
#             'fields': (
#                 ('name', 'manufacturer'),
#                 'description'
#             )
#         }),
#         ('Статистика', {
#             'classes': ('wide',),
#             'fields': ('get_usage_count',),
#             'description': 'Количество станков этой модели на предприятии'
#         }),
#         ('Служебная информация', {
#             'classes': ('collapse',),
#             'fields': ('is_deleted', 'created_at', 'updated_at')
#         }),
#     )
    
#     def machines_count(self, obj):
#         """
#         Количество станков этой модели.
#         """
#         count = obj.machines.count()
#         if count > 0:
#             url = reverse('admin:app_machine_changelist') + f'?model__id__exact={obj.id}'
#             return format_html(
#                 '<a href="{}" style="font-weight: bold;">{} шт.</a>',
#                 url,
#                 count
#             )
#         return format_html('<span style="color: #999;">нет станков</span>')
#     machines_count.short_description = 'Станков в наличии'
    
#     def get_machines_preview(self, obj):
#         """
#         Превью станков этой модели (инвентарные номера).
#         """
#         machines = obj.machines.filter(is_deleted=False)[:3]
#         if machines:
#             preview = ', '.join([m.inventory_number for m in machines])
#             if obj.machines.count() > 3:
#                 preview += f' и ещё {obj.machines.count() - 3}'
#             return format_html('<span title="{}">{}</span>', preview, preview[:30] + '...' if len(preview) > 30 else preview)
#         return '-'
#     get_machines_preview.short_description = 'Станки (превью)'
    
#     def get_usage_count(self, obj):
#         """
#         Количество станков этой модели.
#         """
#         return obj.machines.count()
#     get_usage_count.short_description = 'Количество станков'
    
#     def get_queryset(self, request):
#         """
#         Оптимизируем запросы с помощью select_related и prefetch_related.
#         """
#         return super().get_queryset(request).prefetch_related('machines')


# # ============================================================
# # АДМИНКА ДЛЯ ЦЕХОВ
# # ============================================================

# @admin.register(Workshop)
# class WorkshopAdmin(BaseDictAdmin):
#     """
#     Административный интерфейс для справочника цехов.
    
#     Особенности:
#     - Отображение загрузки цехов
#     - Иерархическая структура (можно добавить parent)
#     - Статистика по станкам в цехе
#     """
    
#     list_display = [
#         'code',
#         'name',
#         'machines_count',
#         'workshop_load',
#         'is_deleted'
#     ]
    
#     list_editable = ['is_deleted']
    
#     list_filter = [
#         'is_deleted',
#         'machines__status',  # Статусы станков в цехе
#         'machines__model',   # Модели станков в цехе
#     ]
    
#     search_fields = ['name', 'code', 'description']
    
#     # Поля для редактирования в форме
#     fieldsets = (
#         ('Основная информация', {
#             'fields': (
#                 'code', 
#                 'name',
#                 'description'
#             )
#         }),
#         ('Служебная информация', {
#             'classes': ('collapse',),
#             'fields': ('is_deleted', 'created_at', 'updated_at')
#         }),
#     )
    
#     def machines_count(self, obj):
#         """
#         Общее количество станков в цехе.
#         """
#         count = obj.machines.count()
#         if count > 0:
#             url = reverse('admin:app_machine_changelist') + f'?workshop__id__exact={obj.id}'
#             return format_html('<a href="{}">{} станков</a>', url, count)
#         return '-'
#     machines_count.short_description = 'Всего станков'
          
#     def workshop_load(self, obj):
#         """
#         Общая загрузка цеха (средний процент загрузки станков).
#         """
#         machines = obj.machines.filter(is_deleted=False)
#         if machines:
#             avg_load = sum(m.load_percent for m in machines) / len(machines)
            
#             # Цветовая индикация загрузки
#             if avg_load > 80:
#                 color = '#dc3545'  # красный - перегрузка
#             elif avg_load > 50:
#                 color = '#ffc107'  # жёлтый - средняя загрузка
#             else:
#                 color = '#28a745'  # зелёный - низкая загрузка
            
#             return format_html(
#                 '<div style="width: 100px; background: #e9ecef; border-radius: 3px;">'
#                 '<div style="width: {}%; background: {}; height: 20px; border-radius: 3px; '
#                 'text-align: center; color: white; font-size: 11px; line-height: 20px;">'
#                 '{:.1f}%</div></div>',
#                 avg_load,
#                 color,
#                 avg_load
#             )
#         return '-'
#     workshop_load.short_description = 'Загрузка цеха'
       
#     def get_queryset(self, request):
#         """
#         Оптимизация запросов.
#         """
#         return super().get_queryset(request).prefetch_related(
#             'machines',
#             'machines__status',
#             'machines__assignments'
#         )
    
#     # Переопределяем метод сохранения для валидации
#     def save_model(self, request, obj, form, change):
#         """
#         Дополнительная валидация при сохранении.
#         """
#         if not obj.code and obj.name:
#             # Автоматически генерируем код из названия, если не указан
#             words = obj.name.split()
#             obj.code = ''.join(word[0].upper() for word in words if word)[:20]
        
#         super().save_model(request, obj, form, change)






# from django.contrib import admin
# from django.utils.html import format_html, format_html_join
# from django.urls import reverse
# from django.db.models import Count, Q, F, Avg, Sum
# from django.utils import timezone
# from django.contrib.admin import SimpleListFilter
# from django.http import HttpResponseRedirect
# from django.shortcuts import redirect
# from .models import Machine, Detail, Stage, MachineAssignment


# # ============================================================
# # КАСТОМНЫЕ ФИЛЬТРЫ
# # ============================================================

# class MachineLoadFilter(SimpleListFilter):
#     """
#     Фильтр для группировки станков по уровню загрузки.
#     """
#     title = 'Уровень загрузки'
#     parameter_name = 'load_level'

#     def lookups(self, request, model_admin):
#         return [
#             ('low', 'Низкая (0-30%)'),
#             ('medium', 'Средняя (31-70%)'),
#             ('high', 'Высокая (71-100%)'),
#         ]

#     def queryset(self, request, queryset):
#         if self.value() == 'low':
#             return queryset.filter(load_percent__lte=30)
#         if self.value() == 'medium':
#             return queryset.filter(load_percent__gt=30, load_percent__lte=70)
#         if self.value() == 'high':
#             return queryset.filter(load_percent__gt=70)
#         return queryset


# class OverdueAssignmentFilter(SimpleListFilter):
#     """
#     Фильтр для просроченных назначений.
#     """
#     title = 'Просрочка'
#     parameter_name = 'overdue'

#     def lookups(self, request, model_admin):
#         return [
#             ('overdue', 'Просроченные'),
#             ('today', 'На сегодня'),
#             ('upcoming', 'Предстоящие'),
#         ]

#     def queryset(self, request, queryset):
#         now = timezone.now()
#         if self.value() == 'overdue':
#             return queryset.filter(
#                 Q(actual_start__isnull=True, planned_start__lt=now) |
#                 Q(actual_start__isnull=False, actual_end__isnull=True, planned_end__lt=now)
#             )
#         if self.value() == 'today':
#             return queryset.filter(
#                 Q(planned_start__date=now.date()) |
#                 Q(planned_end__date=now.date())
#             )
#         if self.value() == 'upcoming':
#             return queryset.filter(
#                 planned_start__gt=now,
#                 actual_start__isnull=True
#             )
#         return queryset


# # ============================================================
# # ИНЛАЙНЫ (для редактирования связанных объектов)
# # ============================================================

# class StageInline(admin.TabularInline):
#     """
#     Инлайн для редактирования этапов прямо в карточке детали.
#     """
#     model = Stage
#     extra = 1
#     fields = [
#         'order_num',
#         'stage_type',
#         'machine',
#         'is_completed',
#         'completion_date',
#         'notes'
#     ]
#     readonly_fields = ['completion_date']
#     autocomplete_fields = ['stage_type', 'machine']
#     ordering = ['order_num']
#     classes = ['collapse']
#     verbose_name = 'Этап обработки'
#     verbose_name_plural = 'Технологический маршрут'


# class AssignmentInline(admin.TabularInline):
#     """
#     Инлайн для назначений на станки.
#     """
#     model = MachineAssignment
#     extra = 0
#     fields = [
#         'machine',
#         'detail',
#         'planned_start',
#         'planned_end',
#         'actual_start',
#         'actual_end',
#         'status_indicator',
#         'notes'
#     ]
#     readonly_fields = ['status_indicator']
#     autocomplete_fields = ['machine', 'detail']
#     ordering = ['-planned_start']
#     classes = ['collapse']
#     verbose_name = 'Назначение'
#     verbose_name_plural = 'Планирование загрузки'

#     def status_indicator(self, obj):
#         """
#         Индикатор статуса назначения.
#         """
#         now = timezone.now()
        
#         if obj.actual_end:
#             return format_html(
#                 '<span style="color: #28a745;">✓ Завершено</span>'
#             )
#         elif obj.actual_start:
#             if obj.planned_end < now:
#                 return format_html(
#                     '<span style="color: #dc3545;">⚠ Просрочено (в работе)</span>'
#                 )
#             return format_html(
#                 '<span style="color: #ffc107;">⟳ В работе</span>'
#             )
#         else:
#             if obj.planned_start < now:
#                 return format_html(
#                     '<span style="color: #dc3545;">⚠ Просрочено (не начато)</span>'
#                 )
#             elif obj.planned_start.date() == now.date():
#                 return format_html(
#                     '<span style="color: #17a2b8;">⌛ На сегодня</span>'
#                 )
#             return format_html(
#                 '<span style="color: #6c757d;">⌚ Запланировано</span>'
#             )
#     status_indicator.short_description = 'Статус'


# # ============================================================
# # АДМИНКА ДЛЯ СТАНКОВ
# # ============================================================

# @admin.register(Machine)
# class MachineAdmin(admin.ModelAdmin):
#     """
#     Административный интерфейс для управления станками.
    
#     Особенности:
#     - Визуальное отображение загрузки
#     - Статистика по назначениям
#     - Быстрый доступ к текущим задачам
#     - Мониторинг состояния оборудования
#     """
    
#     list_display = [
#         'inventory_number',
#         'model_info',
#         'workshop',
#         'status_colored',
#         'load_bar',
#         'current_task',
#         'maintenance_status',
#         'is_deleted'
#     ]
    
#     list_filter = [
#         'workshop',
#         'model',
#         'status',
#         MachineLoadFilter,
#         'is_deleted',
#         ('commissioning_date', admin.DateFieldListFilter),
#         ('last_maintenance_date', admin.DateFieldListFilter),
#     ]
    
#     search_fields = [
#         'inventory_number',
#         'model__name',
#         'model__manufacturer',
#         'workshop__name',
#         'workshop__code',
#         'notes'
#     ]
    
#     autocomplete_fields = ['model', 'workshop', 'status']
    
#     readonly_fields = [
#         'created_at',
#         'updated_at',
#         'assignments_stats',
#         'maintenance_history'
#     ]
    
#     fieldsets = (
#         ('Основная информация', {
#             'fields': (
#                 ('inventory_number', 'model'),
#                 ('workshop', 'status'),
#                 'load_percent',
#                 ('commissioning_date', 'last_maintenance_date'),
#             )
#         }),
#         ('Визуализация загрузки', {
#             'fields': ('assignments_stats'),
#             'classes': ('wide',),
#         }),
#         ('Техническое обслуживание', {
#             'fields': ('maintenance_history',),
#             'classes': ('collapse',),
#         }),
#         ('Служебная информация', {
#             'classes': ('collapse',),
#             'fields': ('is_deleted', 'created_at', 'updated_at')
#         }),
#     )
    
#     actions = ['mark_maintenance_done', 'recalculate_load', 'export_machine_card']
    
#     inlines = [AssignmentInline]
    
#     def get_queryset(self, request):
#         """
#         Оптимизация запросов с предзагрузкой связанных данных.
#         """
#         return super().get_queryset(request).select_related(
#             'model', 'workshop', 'status'
#         ).prefetch_related(
#             'assignments__detail',
#             'stages__detail'
#         )
    
#     def model_info(self, obj):
#         """
#         Отображение информации о модели.
#         """
#         if obj.model.manufacturer:
#             return format_html(
#                 '<strong>{}</strong><br><small style="color: #666;">{}</small>',
#                 obj.model.name,
#                 obj.model.manufacturer
#             )
#         return obj.model.name
#     model_info.short_description = 'Модель'
#     model_info.admin_order_field = 'model__name'
    
#     def status_colored(self, obj):
#         """
#         Цветовое отображение статуса станка.
#         """
#         colors = {
#             'работа': '#28a745',
#             'ремонт': '#dc3545',
#             'ожидание': '#ffc107',
#             'настройка': '#17a2b8',
#             'простой': '#6c757d',
#         }
#         color = colors.get(obj.status.name.lower(), '#6c757d')
        
#         return format_html(
#             '<span style="color: {};">⬤</span> {}',
#             color,
#             obj.status.name
#         )
#     status_colored.short_description = 'Статус'
#     status_colored.admin_order_field = 'status__name'
    
#     def load_bar(self, obj):
#         """
#         Компактная полоса загрузки для списка.
#         """
#         load = float(obj.load_percent)
        
#         if load > 80:
#             color = '#dc3545'
#             bg_color = '#f8d7da'
#         elif load > 50:
#             color = '#ffc107'
#             bg_color = '#fff3cd'
#         else:
#             color = '#28a745'
#             bg_color = '#d4edda'
        
#         return format_html(
#             '<div style="width: 80px; background: {}; border-radius: 3px;">'
#             '<div style="width: {}%; background: {}; height: 20px; border-radius: 3px; '
#             'text-align: center; color: white; font-size: 10px; line-height: 20px;">'
#             '{:.0f}%</div></div>',
#             bg_color,
#             load,
#             color,
#             load
#         )
#     load_bar.short_description = 'Загрузка'
#     load_bar.admin_order_field = 'load_percent'
    
#     def current_task(self, obj):
#         """
#         Текущая задача на станке.
#         """
#         current = obj.assignments.filter(
#             actual_start__isnull=False,
#             actual_end__isnull=True
#         ).first()
        
#         if current:
#             url = reverse('admin:app_detail_change', args=[current.detail.id])
#             return format_html(
#                 '<a href="{}">{}<br><small>до {}</small></a>',
#                 url,
#                 current.detail.article,
#                 current.planned_end.strftime('%d.%m.%Y %H:%M')
#             )
#         return '-'
#     current_task.short_description = 'Текущая задача'
    
#     def maintenance_status(self, obj):
#         """
#         Статус технического обслуживания.
#         """
#         if not obj.last_maintenance_date:
#             return format_html('<span style="color: #dc3545;">⚠ ТО не проводилось</span>')
        
#         days_since = (timezone.now().date() - obj.last_maintenance_date).days
        
#         if days_since > 365:
#             return format_html('<span style="color: #dc3545;">⚠ Требуется ТО (>{})</span>', '1 год')
#         elif days_since > 180:
#             return format_html('<span style="color: #ffc107;">⚠ Скоро ТО ({} дн.)</span>', days_since)
#         else:
#             return format_html('<span style="color: #28a745;">✓ ОК ({} дн.)</span>', days_since)
#     maintenance_status.short_description = 'Состояние ТО'
    
#     def maintenance_history(self, obj):
#         """
#         История обслуживания станка.
#         """
#         if not obj.last_maintenance_date:
#             return "Нет данных о ТО"
        
#         next_maintenance = obj.last_maintenance_date + timezone.timedelta(days=365)
#         days_until = (next_maintenance - timezone.now().date()).days
        
#         return format_html(
#             '<div>'
#             '<p><strong>Последнее ТО:</strong> {}</p>'
#             '<p><strong>Следующее ТО:</strong> {} (через {} дней)</p>'
#             '<p><strong>В эксплуатации:</strong> {} лет</p>'
#             '</div>',
#             obj.last_maintenance_date.strftime('%d.%m.%Y'),
#             next_maintenance.strftime('%d.%m.%Y'),
#             days_until,
#             (timezone.now().date() - obj.commissioning_date).days // 365 if obj.commissioning_date else 'N/A'
#         )
#     maintenance_history.short_description = 'История ТО'
    
#     def mark_maintenance_done(self, request, queryset):
#         """
#         Отметить выполнение ТО для выбранных станков.
#         """
#         updated = queryset.update(
#             last_maintenance_date=timezone.now().date(),
#             updated_at=timezone.now()
#         )
#         self.message_user(request, f'Отмечено выполнение ТО для {updated} станков')
#     mark_maintenance_done.short_description = 'Отметить выполнение ТО'


# # ============================================================
# # АДМИНКА ДЛЯ ДЕТАЛЕЙ
# # ============================================================

# @admin.register(Detail)
# class DetailAdmin(admin.ModelAdmin):
#     """
#     Административный интерфейс для управления деталями.
    
#     Особенности:
#     - Отображение процента готовности с индикатором
#     - Технологический маршрут inline
#     - История изменений статуса
#     - Кнопка ручного пересчёта готовности
#     """
    
#     list_display = [
#         'article',
#         'name',
#         'drawing_number',
#         'status_colored',
#         'completion_bar',
#         'planned_date_colored',
#         'stages_count',
#         'current_stage'
#     ]
    
#     list_filter = [
#         'status',
#         'is_deleted',
#         ('planned_completion_date', admin.DateFieldListFilter),
#     ]
    
#     search_fields = [
#         'article',
#         'name',
#         'drawing_number',
#         'description'
#     ]
    
#     readonly_fields = [
#         'completion_percent',
#         'created_at',
#         'updated_at',
#         'completion_history',
#         'stages_timeline'
#     ]
    
#     fieldsets = (
#         ('Основная информация', {
#             'fields': (
#                 ('article', 'name'),
#                 ('drawing_number', 'planned_completion_date'),
#                 'status',
#                 'description'
#             )
#         }),
#         ('Готовность', {
#             'fields': ('completion_percent', 'completion_history'),
#             'classes': ('wide',),
#         }),
#         ('Технологический маршрут', {
#             'fields': ('stages_timeline',),
#             'classes': ('wide',),
#         }),
#         ('Служебная информация', {
#             'classes': ('collapse',),
#             'fields': ('is_deleted', 'created_at', 'updated_at')
#         }),
#     )
    
#     actions = ['recalculate_completion', 'mark_as_ready', 'export_detail_card']
    
#     inlines = [StageInline, AssignmentInline]
    
#     def get_queryset(self, request):
#         """
#         Оптимизация запросов.
#         """
#         return super().get_queryset(request).select_related(
#             'status'
#         ).prefetch_related(
#             'stages__stage_type',
#             'stages__machine'
#         )
    
#     def status_colored(self, obj):
#         """
#         Цветовое отображение статуса.
#         """
#         colors = {
#             'в работе': '#28a745',
#             'завершено': '#17a2b8',
#             'ожидание': '#ffc107',
#             'брак': '#dc3545',
#         }
#         color = colors.get(obj.status.name.lower(), '#6c757d')
        
#         return format_html(
#             '<span style="color: {};">⬤</span> {}',
#             color,
#             obj.status.name
#         )
#     status_colored.short_description = 'Статус'
    
#     def completion_bar(self, obj):
#         """
#         Индикатор процента готовности.
#         """
#         percent = float(obj.completion_percent)
        
#         if percent >= 100:
#             color = '#28a745'
#             bg_color = '#d4edda'
#         elif percent >= 70:
#             color = '#ffc107'
#             bg_color = '#fff3cd'
#         else:
#             color = '#dc3545'
#             bg_color = '#f8d7da'
        
#         return format_html(
#             '<div style="width: 100px; background: {}; border-radius: 3px;">'
#             '<div style="width: {}%; background: {}; height: 20px; border-radius: 3px; '
#             'text-align: center; color: white; font-size: 10px; line-height: 20px;">'
#             '{:.0f}%</div></div>',
#             bg_color,
#             min(percent, 100),
#             color,
#             percent
#         )
#     completion_bar.short_description = 'Готовность'
#     completion_bar.admin_order_field = 'completion_percent'
    
#     def planned_date_colored(self, obj):
#         """
#         Цветовое отображение плановой даты.
#         """
#         if not obj.planned_completion_date:
#             return '-'
        
#         now = timezone.now()
#         if obj.completion_percent >= 100:
#             return format_html(
#                 '<span style="color: #28a745;">✓ {}</span>',
#                 obj.planned_completion_date.strftime('%d.%m.%Y')
#             )
        
#         if obj.planned_completion_date < now:
#             return format_html(
#                 '<span style="color: #dc3545; font-weight: bold;">⚠ {} (просрочено)</span>',
#                 obj.planned_completion_date.strftime('%d.%m.%Y')
#             )
        
#         days_left = (obj.planned_completion_date - now).days
#         if days_left <= 3:
#             return format_html(
#                 '<span style="color: #ffc107;">⚠ {} (осталось {} дн.)</span>',
#                 obj.planned_completion_date.strftime('%d.%m.%Y'),
#                 days_left
#             )
        
#         return obj.planned_completion_date.strftime('%d.%m.%Y')
#     planned_date_colored.short_description = 'Плановая дата'
    
#     def stages_count(self, obj):
#         """
#         Количество этапов.
#         """
#         total = obj.stages.count()
#         completed = obj.stages.filter(is_completed=True).count()
        
#         return format_html(
#             '<span title="Выполнено {}/{}">{}/{}</span>',
#             completed,
#             total,
#             completed,
#             total
#         )
#     stages_count.short_description = 'Этапы'
    
#     def current_stage(self, obj):
#         """
#         Текущий этап обработки.
#         """
#         current = obj.stages.filter(
#             is_completed=False
#         ).order_by('order_num').first()
        
#         if current:
#             return format_html(
#                 '{}<br><small>Станок: {}</small>',
#                 current.stage_type.name,
#                 current.machine.inventory_number if current.machine else '-'
#             )
#         return '✓ Завершено'
#     current_stage.short_description = 'Текущий этап'
    
#     def completion_history(self, obj):
#         """
#         История изменения готовности (можно добавить отдельную модель для истории).
#         """
#         return format_html(
#             '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">'
#             '<p><strong>Текущая готовность:</strong> {}%</p>'
#             '<p><strong>Выполнено этапов:</strong> {} из {}</p>'
#             '<p><strong>Осталось этапов:</strong> {}</p>'
#             '</div>',
#             obj.completion_percent,
#             obj.stages.filter(is_completed=True).count(),
#             obj.stages.count(),
#             obj.stages.filter(is_completed=False).count()
#         )
#     completion_history.short_description = 'Статистика готовности'
    
#     def stages_timeline(self, obj):
#         """
#         Визуальная временная шкала этапов.
#         """
#         stages = obj.stages.all().order_by('order_num')
        
#         if not stages:
#             return "Нет этапов"
        
#         timeline = []
#         for stage in stages:
#             if stage.is_completed:
#                 bg_color = '#d4edda'
#                 border_color = '#28a745'
#                 icon = '✓'
#                 status = 'Выполнен'
#             else:
#                 bg_color = '#fff3cd'
#                 border_color = '#ffc107'
#                 icon = '○'
#                 status = 'Ожидание'
            
#             stage_html = format_html(
#                 '<div style="display: inline-block; width: 120px; margin: 5px; padding: 8px; '
#                 'background: {}; border-left: 4px solid {}; border-radius: 3px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">'
#                 '<div style="font-size: 16px; font-weight: bold;">{} #{}</div>'
#                 '<div style="font-size: 12px;">{}</div>'
#                 '<div style="font-size: 10px; color: #666; margin-top: 5px;">'
#                 '<span>{}</span><br>'
#                 '<span>{}</span>'
#                 '</div>'
#                 '</div>',
#                 bg_color,
#                 border_color,
#                 icon,
#                 stage.order_num,
#                 stage.stage_type.name,
#                 status,
#                 stage.machine.inventory_number if stage.machine else 'Станок не назначен'
#             )
#             timeline.append(stage_html)
        
#         return format_html_join('\n', '{}', [(t,) for t in timeline])
#     stages_timeline.short_description = 'Технологический маршрут'
    
#     def recalculate_completion(self, request, queryset):
#         """
#         Пересчитать готовность для выбранных деталей.
#         """
#         for detail in queryset:
#             detail.recalculate_completion()
        
#         self.message_user(
#             request,
#             f'Готовность пересчитана для {queryset.count()} деталей'
#         )
#     recalculate_completion.short_description = 'Пересчитать готовность'
    
#     def mark_as_ready(self, request, queryset):
#         """
#         Отметить детали как готовые.
#         """
#         ready_status = Status.objects.filter(name__icontains='готов').first()
#         if ready_status:
#             updated = queryset.update(
#                 status=ready_status,
#                 completion_percent=100
#             )
#             self.message_user(request, f'{updated} деталей отмечены как готовые')
#         else:
#             self.message_user(
#                 request,
#                 'Не найден статус "Готово"',
#                 level='ERROR'
#             )
#     mark_as_ready.short_description = 'Отметить как готовые'
    
#     def export_detail_card(self, request, queryset):
#         """
#         Экспорт карточки детали.
#         """
#         self.message_user(request, 'Функция экспорта в разработке')
#     export_detail_card.short_description = 'Экспорт карточки'


# # ============================================================
# # АДМИНКА ДЛЯ ЭТАПОВ
# # ============================================================

# @admin.register(Stage)
# class StageAdmin(admin.ModelAdmin):
#     """
#     Административный интерфейс для управления этапами.
    
#     Особенности:
#     - Управление технологическим маршрутом
#     - Массовая отметка выполнения
#     - Контроль последовательности
#     """
    
#     list_display = [
#         'detail_link',
#         'order_num',
#         'stage_type',
#         'machine_info',
#         'status_indicator',
#         'completion_date_colored'
#     ]
    
#     list_filter = [
#         'is_completed',
#         'stage_type',
#         'machine__workshop',
#         'is_deleted'
#     ]
    
#     search_fields = [
#         'detail__article',
#         'detail__name',
#         'stage_type__name',
#         'machine__inventory_number',
#         'notes'
#     ]
    
#     autocomplete_fields = ['detail', 'stage_type', 'machine']
    
#     readonly_fields = ['completion_date', 'created_at', 'updated_at']
    
#     fieldsets = (
#         (None, {
#             'fields': (
#                 ('detail', 'stage_type'),
#                 ('order_num', 'machine'),
#                 ('is_completed', 'completion_date'),
#                 'notes'
#             )
#         }),
#         ('Служебная информация', {
#             'classes': ('collapse',),
#             'fields': ('is_deleted', 'created_at', 'updated_at')
#         }),
#     )
    
#     actions = ['mark_completed', 'mark_not_completed', 'reorder_stages']
    
#     def get_queryset(self, request):
#         """
#         Оптимизация запросов.
#         """
#         return super().get_queryset(request).select_related(
#             'detail', 'stage_type', 'machine'
#         )
    
#     def detail_link(self, obj):
#         """
#         Ссылка на карточку детали.
#         """
#         url = reverse('admin:app_detail_change', args=[obj.detail.id])
#         return format_html(
#             '<a href="{}">{}<br><small>{}</small></a>',
#             url,
#             obj.detail.article,
#             obj.detail.name[:30] + '...' if len(obj.detail.name) > 30 else obj.detail.name
#         )
#     detail_link.short_description = 'Деталь'
    
#     def machine_info(self, obj):
#         """
#         Информация о станке.
#         """
#         if obj.machine:
#             return format_html(
#                 '{}<br><small>{}</small>',
#                 obj.machine.inventory_number,
#                 obj.machine.workshop.code if obj.machine.workshop else '-'
#             )
#         return '-'
#     machine_info.short_description = 'Станок'
    
#     def status_indicator(self, obj):
#         """
#         Индикатор выполнения этапа.
#         """
#         if obj.is_completed:
#             return format_html(
#                 '<span style="color: #28a745;">✓ Выполнен</span>'
#             )
#         return format_html(
#             '<span style="color: #ffc107;">○ Ожидание</span>'
#         )
#     status_indicator.short_description = 'Статус'
    
#     def completion_date_colored(self, obj):
#         """
#         Цветовое отображение даты выполнения.
#         """
#         if obj.completion_date:
#             return format_html(
#                 '<span style="color: #28a745;">{}</span>',
#                 obj.completion_date.strftime('%d.%m.%Y %H:%M')
#             )
#         return '-'
#     completion_date_colored.short_description = 'Дата выполнения'
    
#     def mark_completed(self, request, queryset):
#         """
#         Отметить этапы как выполненные.
#         """
#         now = timezone.now()
#         updated = queryset.update(
#             is_completed=True,
#             completion_date=now
#         )
        
#         # Обновляем проценты готовности деталей
#         for stage in queryset:
#             stage.detail.recalculate_completion()
        
#         self.message_user(request, f'Отмечено как выполненные: {updated} этапов')
#     mark_completed.short_description = 'Отметить как выполненные'
    
#     def mark_not_completed(self, request, queryset):
#         """
#         Снять отметку выполнения.
#         """
#         updated = queryset.update(
#             is_completed=False,
#             completion_date=None
#         )
        
#         for stage in queryset:
#             stage.detail.recalculate_completion()
        
#         self.message_user(request, f'Снята отметка выполнения: {updated} этапов')
#     mark_not_completed.short_description = 'Снять отметку выполнения'
    
#     def reorder_stages(self, request, queryset):
#         """
#         Перенумеровать этапы по порядку.
#         """
#         details = set(queryset.values_list('detail', flat=True))
        
#         for detail_id in details:
#             stages = Stage.objects.filter(detail_id=detail_id).order_by('order_num', 'id')
#             for i, stage in enumerate(stages, 1):
#                 if stage.order_num != i:
#                     stage.order_num = i
#                     stage.save()
        
#         self.message_user(request, 'Этапы перенумерованы')
#     reorder_stages.short_description = 'Перенумеровать этапы'


# # ============================================================
# # АДМИНКА ДЛЯ НАЗНАЧЕНИЙ
# # ============================================================

# @admin.register(MachineAssignment)
# class MachineAssignmentAdmin(admin.ModelAdmin):
#     """
#     Административный интерфейс для назначений на станки.
    
#     Особенности:
#     - Планирование загрузки
#     - Отметка фактического начала/окончания
#     - Контроль просрочек
#     - Ганта-диаграмма (текстовая)
#     """
    
#     list_display = [
#         'machine_link',
#         'detail_link',
#         'planned_period',
#         'actual_status',
#         'progress_indicator',
#         'overdue_indicator'
#     ]
    
#     list_filter = [
#         OverdueAssignmentFilter,
#         'machine__workshop',
#         'machine',
#         'actual_start__isnull',
#         'actual_end__isnull',
#     ]
    
#     search_fields = [
#         'machine__inventory_number',
#         'detail__article',
#         'detail__name',
#         'notes'
#     ]
    
#     autocomplete_fields = ['machine', 'detail']
    
#     readonly_fields = ['assignment_date', 'created_at', 'updated_at', 'duration_calc']
    
#     fieldsets = (
#         ('Назначение', {
#             'fields': (
#                 ('machine', 'detail'),
#                 ('planned_start', 'planned_end'),
#                 ('actual_start', 'actual_end'),
#                 'notes'
#             )
#         }),
#         ('Расчётное время', {
#             'fields': ('duration_calc',),
#             'classes': ('collapse',),
#         }),
#         ('Служебная информация', {
#             'classes': ('collapse',),
#             'fields': ('assignment_date', 'created_at', 'updated_at', 'is_deleted')
#         }),
#     )
    
#     actions = ['start_now', 'complete_now', 'duplicate_assignment']
    
#     def get_queryset(self, request):
#         """
#         Оптимизация запросов.
#         """
#         return super().get_queryset(request).select_related(
#             'machine', 'detail'
#         )
    
#     def machine_link(self, obj):
#         """
#         Ссылка на станок.
#         """
#         url = reverse('admin:app_machine_change', args=[obj.machine.id])
#         return format_html(
#             '<a href="{}">{}<br><small>{}</small></a>',
#             url,
#             obj.machine.inventory_number,
#             obj.machine.workshop.code if obj.machine.workshop else '-'
#         )
#     machine_link.short_description = 'Станок'
    
#     def detail_link(self, obj):
#         """
#         Ссылка на деталь.
#         """
#         url = reverse('admin:app_detail_change', args=[obj.detail.id])
#         return format_html(
#             '<a href="{}">{}<br><small>{}</small></a>',
#             url,
#             obj.detail.article,
#             obj.detail.name[:30] + '...' if len(obj.detail.name) > 30 else obj.detail.name
#         )
#     detail_link.short_description = 'Деталь'
    
#     def planned_period(self, obj):
#         """
#         Плановый период.
#         """
#         return format_html(
#             '{} → {}<br><small>{} дн.</small>',
#             obj.planned_start.strftime('%d.%m.%Y'),
#             obj.planned_end.strftime('%d.%m.%Y'),
#             (obj.planned_end - obj.planned_start).days
#         )
#     planned_period.short_description = 'Плановый период'
    
#     def actual_status(self, obj):
#         """
#         Статус выполнения.
#         """
#         if obj.actual_end:
#             return format_html(
#                 '<span style="color: #28a745;">✓ Завершено<br><small>{}</small></span>',
#                 obj.actual_end.strftime('%d.%m.%Y %H:%M')
#             )
#         elif obj.actual_start:
#             return format_html(
#                 '<span style="color: #ffc107;">⟳ В работе<br><small>с {}</small></span>',
#                 obj.actual_start.strftime('%d.%m.%Y %H:%M')
#             )
#         else:
#             return format_html(
#                 '<span style="color: #6c757d;">⌚ Ожидание</span>'
#             )
#     actual_status.short_description = 'Фактический статус'
    
#     def progress_indicator(self, obj):
#         """
#         Индикатор прогресса выполнения.
#         """
#         now = timezone.now()
        
#         if obj.actual_end:
#             return format_html('✓ 100%')
#         elif obj.actual_start:
#             total_days = (obj.planned_end - obj.planned_start).days
#             if total_days == 0:
#                 return format_html('⟳ в работе')
            
#             elapsed = (now - obj.actual_start).days
#             progress = min(int((elapsed / total_days) * 100), 99)
            
#             return format_html(
#                 '<div style="width: 80px; background: #e9ecef; border-radius: 3px;">'
#                 '<div style="width: {}%; background: #ffc107; height: 20px; border-radius: 3px; '
#                 'text-align: center; color: black; font-size: 10px; line-height: 20px;">'
#                 '{}%</div></div>',
#                 progress,
#                 progress
#             )
#         else:
#             return format_html('<span style="color: #999;">0%</span>')
#     progress_indicator.short_description = 'Прогресс'
    
#     def overdue_indicator(self, obj):
#         """
#         Индикатор просрочки.
#         """
#         now = timezone.now()
        
#         if obj.actual_end:
#             return ''
        
#         if obj.actual_start:
#             if obj.planned_end < now:
#                 days = (now - obj.planned_end).days
#                 return format_html(
#                     '<span style="color: #dc3545;" title="Просрочка {} дн.">⚠ {} дн.</span>',
#                     days,
#                     days
#                 )
#         else:
#             if obj.planned_start < now:
#                 days = (now - obj.planned_start).days
#                 return format_html(
#                     '<span style="color: #dc3545;" title="Не начато, просрочка {} дн.">⚠ {} дн.</span>',
#                     days,
#                     days
#                 )
#         return ''
#     overdue_indicator.short_description = 'Просрочка'
    
#     def duration_calc(self, obj):
#         """
#         Расчёт длительности.
#         """
#         if obj.actual_start and obj.actual_end:
#             duration = obj.actual_end - obj.actual_start
#             return f'Фактическая длительность: {duration.days} дн. {duration.seconds // 3600} ч.'
#         elif obj.actual_start:
#             elapsed = timezone.now() - obj.actual_start
#             return f'В работе: {elapsed.days} дн. {elapsed.seconds // 3600} ч.'
#         else:
#             planned = obj.planned_end - obj.planned_start
#             return f'Плановая длительность: {planned.days} дн. {planned.seconds // 3600} ч.'
#     duration_calc.short_description = 'Длительность'
    
#     def start_now(self, request, queryset):
#         """
#         Отметить фактическое начало.
#         """
#         now = timezone.now()
#         updated = queryset.filter(actual_start__isnull=True).update(actual_start=now)
#         self.message_user(request, f'Отмечено начало работ: {updated} назначений')
#     start_now.short_description = 'Отметить начало'
    
#     def complete_now(self, request, queryset):
#         """
#         Отметить фактическое завершение.
#         """
#         now = timezone.now()
#         updated = queryset.filter(actual_end__isnull=True).update(
#             actual_end=now,
#             actual_start=models.F('actual_start') or now
#         )
#         self.message_user(request, f'Отмечено завершение: {updated} назначений')
#     complete_now.short_description = 'Отметить завершение'
    
#     def duplicate_assignment(self, request, queryset):
#         """
#         Дублировать назначение.
#         """
#         for assignment in queryset:
#             assignment.pk = None
#             assignment.assignment_date = timezone.now()
#             assignment.actual_start = None
#             assignment.actual_end = None
#             assignment.planned_start += timezone.timedelta(days=1)
#             assignment.planned_end += timezone.timedelta(days=1)
#             assignment.save()
        
#         self.message_user(request, f'Создано дубликатов: {queryset.count()}')
#     duplicate_assignment.short_description = 'Дублировать с переносом на день'