from django import template
from datetime import timedelta
from django.utils import timezone
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def add_days(value, days):
    """
    Добавляет указанное количество дней к дате
    Использование: {{ value|add_days:3 }}
    """
    if not value:
        return value
    try:
        return value + timedelta(days=int(days))
    except (ValueError, TypeError):
        return value

@register.filter
def time_until(value):
    """
    Возвращает время до указанной даты в человекочитаемом формате
    Использование: {{ value|time_until }}
    НЕ ИСПОЛЬЗУЙТЕ timeuntil - это встроенный фильтр Django!
    """
    if not value:
        return ''
    
    now = timezone.now()
    if value < now:
        return 'просрочено'
    
    return timesince(now, value)

@register.simple_tag
def current_time():
    """
    Возвращает текущее время
    Использование: {% current_time %}
    """
    return timezone.now()

@register.filter
def is_overdue(value):
    """
    Проверяет, просрочена ли дата
    Использование: {% if value|is_overdue %}...{% endif %}
    """
    if not value:
        return False
    return value < timezone.now()

@register.filter
def days_until(value):
    """
    Возвращает количество дней до даты
    Использование: {{ value|days_until }}
    """
    if not value:
        return ''
    
    now = timezone.now()
    if value < now:
        return 0
    
    delta = value - now
    return delta.days

@register.filter
def format_planned_date(value):
    """
    Форматирует плановую дату с цветовым кодом
    Использование: {{ value|format_planned_date|safe }}
    Возвращает HTML с классом для стилизации
    """
    if not value:
        return '<span class="text-muted">—</span>'
    
    now = timezone.now()
    if value < now:
        return f'<span class="planned-date overdue">{value|date:"d.m.Y"}</span>'
    elif value < now + timedelta(days=3):
        return f'<span class="planned-date warning">{value|date:"d.m.Y"}</span>'
    else:
        return f'<span class="planned-date">{value|date:"d.m.Y"}</span>'