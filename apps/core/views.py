from django.shortcuts import render

from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from django.db.models import Q, Count, F, Value, IntegerField, Case, When, Avg
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.utils import timezone

from datetime import datetime, timedelta

from .models import (
    Detail, Status, Stage, Workshop, Machine
)




def dashboard(request):

    return render(

        request,

        "dashboard/dashboard.html"

    )




def detail_list(request):
    """
    View для отображения списка деталей с использованием DataTables.
    """
    # Базовый queryset с оптимизацией запросов
    details = Detail.objects.select_related(
        'status'
    ).prefetch_related(
        'stages__stage_type',
        'stages__machine'
    ).filter(is_deleted=False)
    
    # Аннотируем дополнительную информацию
    details = details.annotate(
        total_stages=Count('stages', filter=Q(stages__is_deleted=False)),
        completed_stages=Count('stages', filter=Q(stages__is_completed=True, stages__is_deleted=False)),
        current_stage_order=Coalesce(
            F('stages__order_num'),
            Value(0),
            output_field=IntegerField()
        )
    )
    
    # Добавляем информацию о текущем этапе
    for detail in details:
        detail.current_stage = detail.stages.filter(
            is_completed=False
        ).order_by('order_num').first()
    
    # Статистика для метрик
    total_details = details.count()
    completed_details = details.filter(status__name__icontains='готов').count()
    in_progress_details = details.filter(status__name__icontains='работе').count()
    
    # Просроченные детали
    now = datetime.now()
    overdue_details = details.filter(
        planned_completion_date__lt=now,
        status__name__icontains='готов'
    ).count()
    
    # Получаем справочники для фильтров
    statuses = Status.objects.filter(
        Q(details__isnull=False) | Q(machines__isnull=False)
    ).distinct().order_by('name')
    
    workshops = Workshop.objects.filter(
        machines__stages__detail__isnull=False
    ).distinct().order_by('name')
    
    # Средний процент готовности
    avg_completion = details.aggregate(avg=Avg('completion_percent'))['avg'] or 0
    
    context = {
        'details': details,
        'total_details': total_details,
        'completed_details': completed_details,
        'in_progress_details': in_progress_details,
        'overdue_details': overdue_details,
        'avg_completion': round(avg_completion, 1),
        'statuses': statuses,
        'workshops': workshops,
    }
    
    return render(request, 'details/detail_list.html', context)



def detail_card(request,id):

    detail = Detail.objects.get(id=id)

    stages = detail.stages.all()

    return render(

        request,

        "details/detail_card.html",

        {

            "detail":detail,

            "stages":stages

        }

    )


from django.shortcuts import render
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Machine, MachineAssignment, Workshop, Status, MachineModel

def machine_list(request):
    """
    View для отображения списка станков с использованием DataTables.
    """
    # Базовый queryset с оптимизацией запросов
    machines = Machine.objects.select_related(
        'model', 'workshop', 'status'
    ).prefetch_related(
        'assignments__detail',  # через MachineAssignment
        'stages__detail'        # через Stage
    ).filter(is_deleted=False)
    
    # Аннотируем дополнительную информацию через related_name из моделей
    machines = machines.annotate(
        active_assignments=Count(
            'assignments',  # related_name из MachineAssignment.machine
            filter=Q(
                assignments__actual_start__isnull=False,
                assignments__actual_end__isnull=True,
                assignments__is_deleted=False
            )
        ),
        total_assignments=Count(
            'assignments',  # related_name из MachineAssignment.machine
            filter=Q(assignments__is_deleted=False)
        ),
        completed_assignments=Count(
            'assignments',  # related_name из MachineAssignment.machine
            filter=Q(
                assignments__actual_end__isnull=False,
                assignments__is_deleted=False
            )
        ),
        total_stages=Count(
            'stages',  # related_name из Stage.machine
            filter=Q(stages__is_deleted=False)
        ),
        active_stages=Count(
            'stages',  # related_name из Stage.machine
            filter=Q(
                stages__is_completed=False,
                stages__is_deleted=False
            )
        )
    )
    
    # Добавляем информацию о текущей задаче
    now = timezone.now()
    for machine in machines:
        # Текущее назначение (в работе) через related_name 'assignments'
        current_assignment = machine.assignments.filter(
            actual_start__isnull=False,
            actual_end__isnull=True,
            is_deleted=False
        ).select_related('detail').first()
        
        if current_assignment:
            machine.current_detail = current_assignment.detail
            machine.current_assignment = current_assignment
        else:
            # Следующее назначение в очереди
            next_assignment = machine.assignments.filter(
                actual_start__isnull=True,
                planned_start__gte=now,
                is_deleted=False
            ).order_by('planned_start').select_related('detail').first()
            
            if next_assignment:
                machine.next_detail = next_assignment.detail
                machine.next_assignment = next_assignment
        
        # Текущий этап на станке
        current_stage = machine.stages.filter(
            is_completed=False,
            is_deleted=False
        ).select_related('detail', 'stage_type').first()
        
        if current_stage:
            machine.current_stage_detail = current_stage.detail
            machine.current_stage_type = current_stage.stage_type
        
        # Проверка на необходимость ТО
        if machine.last_maintenance_date:
            days_since_maintenance = (now.date() - machine.last_maintenance_date).days
            if days_since_maintenance < 180:
                machine.maintenance_status = 'ok'
            elif days_since_maintenance < 365:
                machine.maintenance_status = 'warning'
            else:
                machine.maintenance_status = 'danger'
        else:
            machine.maintenance_status = 'danger'
    
    # Статистика для метрик
    total_machines = machines.count()
    active_machines = machines.filter(status__name__icontains='работа').count()
    idle_machines = machines.filter(status__name__icontains='ожида').count()
    maintenance_machines = machines.filter(
        Q(status__name__icontains='ремонт') | 
        Q(status__name__icontains='неисправ')
    ).count()
    
    # Средняя загрузка
    avg_load = machines.aggregate(avg=Avg('load_percent'))['avg'] or 0
    
    # Станки с высокой загрузкой (>80%)
    high_load_machines = machines.filter(load_percent__gt=80).count()
    
    # Получаем справочники для фильтров
    workshops = Workshop.objects.filter(
        machines__isnull=False  # related_name из Machine.workshop
    ).distinct().order_by('name')
    
    # Для моделей используем связанное имя 'machines' из модели MachineModel
    models = MachineModel.objects.filter(
        machines__isnull=False  # related_name из Machine.model
    ).distinct().order_by('name')
    
    # Для статусов используем связанное имя 'machines' из модели Status
    statuses = Status.objects.filter(
        machines__isnull=False  # related_name из Machine.status
    ).distinct().order_by('name')
    
    context = {
        'machines': machines,
        'total_machines': total_machines,
        'active_machines': active_machines,
        'idle_machines': idle_machines,
        'maintenance_machines': maintenance_machines,
        'avg_load': round(avg_load, 1),
        'high_load_machines': high_load_machines,
        'workshops': workshops,
        'models': models,
        'statuses': statuses,
        'now': now,
    }
    
    return render(request, 'machines/machine_list.html', context)


@require_GET
def available_details(request):
    """Возвращает список доступных для назначения деталей"""
    details = Detail.objects.filter(
        is_deleted=False,
        completion_percent__lt=100
    ).values('id', 'article', 'name')[:50]
    
    return JsonResponse(list(details), safe=False)

@require_GET
def machines_load(request):
    """Возвращает текущую загрузку станков"""
    machines = Machine.objects.filter(
        is_deleted=False
    ).values('inventory_number', 'load_percent')
    
    data = [{
        'inventory': m['inventory_number'],
        'load': float(m['load_percent'])
    } for m in machines]
    
    return JsonResponse(data, safe=False)