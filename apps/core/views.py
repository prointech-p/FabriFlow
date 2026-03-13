from django.shortcuts import render, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import (
    Q, Count, F, 
    Value, IntegerField, Case, When, 
    Avg, DurationField, ExpressionWrapper,
    OuterRef, Subquery
)
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from datetime import datetime, timedelta

from .models import (
    Detail, 
    Status, 
    Stage, 
    StageType,
    Workshop, 
    MachineModel,
    Machine,
    MachineAssignment
)

def get_completed_status():
    """
    Получение статуса, соответствующего готовности.
    """
    status = Status.objects.filter(name='Завершено').first()
    return status


def dashboard(request):
    """
    View для отображения дашборда с графиками и сводной информацией.
    """
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # ==================== СТАТИСТИКА ПО ДЕТАЛЯМ ====================
    details_stats = {
        'total': Detail.objects.filter(is_deleted=False).count(),
        'completed': Detail.objects.filter(
            is_deleted=False,
            status__name__icontains='готов'
        ).count(),
        'in_progress': Detail.objects.filter(
            is_deleted=False,
            status__name__icontains='работе'
        ).count(),
        'overdue': Detail.objects.filter(
            is_deleted=False,
            planned_completion_date__lt=now,
            completion_percent__lt=100
        ).exclude(
            status__name__icontains='готов'
        ).count(),
    }
    
    # Средний процент готовности
    avg_completion = Detail.objects.filter(
        is_deleted=False
    ).aggregate(avg=Avg('completion_percent'))['avg'] or 0
    details_stats['avg_completion'] = round(avg_completion, 1)
    
    # ==================== СТАТИСТИКА ПО СТАНКАМ ====================
    # ИСПРАВЛЕНО: правильное использование Q объектов
    machines_stats = {
        'total': Machine.objects.filter(is_deleted=False).count(),
        'active': Machine.objects.filter(
            is_deleted=False,
            status__name__icontains='работа'
        ).count(),
        'idle': Machine.objects.filter(
            is_deleted=False,
            status__name__icontains='ожида'
        ).count(),
        'maintenance': Machine.objects.filter(
            is_deleted=False
        ).filter(
            Q(status__name__icontains='ремонт') | 
            Q(status__name__icontains='неисправ')
        ).count(),
    }
    
    # Средняя загрузка станков
    avg_load = Machine.objects.filter(
        is_deleted=False
    ).aggregate(avg=Avg('load_percent'))['avg'] or 0
    machines_stats['avg_load'] = round(avg_load, 1)
    
    # Станки с высокой загрузкой (>80%)
    machines_stats['high_load'] = Machine.objects.filter(
        is_deleted=False,
        load_percent__gt=80
    ).count()
    
    # ==================== СТАТИСТИКА ПО ЭТАПАМ ====================
    stages_stats = {
        'total': Stage.objects.filter(is_deleted=False).count(),
        'completed': Stage.objects.filter(
            is_deleted=False,
            is_completed=True
        ).count(),
        'in_progress': Stage.objects.filter(
            is_deleted=False,
            is_completed=False,
            machine__isnull=False,
            machine__assignments__actual_start__isnull=False,
            machine__assignments__actual_end__isnull=True
        ).distinct().count(),
        'pending': Stage.objects.filter(
            is_deleted=False,
            is_completed=False,
            machine__isnull=True
        ).count(),
    }
    
    # ==================== ГРАФИК ЗАГРУЗКИ СТАНКОВ ====================
    # Данные для круговой диаграммы загрузки
    machine_load_data = {
        'high': Machine.objects.filter(is_deleted=False, load_percent__gt=80).count(),
        'medium': Machine.objects.filter(is_deleted=False, load_percent__range=(30, 80)).count(),
        'low': Machine.objects.filter(is_deleted=False, load_percent__lt=30).count(),
    }
    
    # Данные для графика загрузки по цехам
    workshops_load = []
    workshops = Workshop.objects.filter(machines__is_deleted=False).distinct()
    for workshop in workshops:
        machines_in_workshop = workshop.machines.filter(is_deleted=False)
        if machines_in_workshop.exists():
            avg_workshop_load = machines_in_workshop.aggregate(avg=Avg('load_percent'))['avg'] or 0
            workshops_load.append({
                'name': workshop.name,
                'load': round(avg_workshop_load, 1),
                'total': machines_in_workshop.count(),
                'active': machines_in_workshop.filter(status__name__icontains='работа').count()
            })
    
    # ==================== ГРАФИК ВЫПОЛНЕНИЯ ЭТАПОВ ПО ДНЯМ ====================
    # Последние 7 дней
    last_7_days = []
    completed_by_day = []
    
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day, tzinfo=now.tzinfo)
        day_end = day_start + timedelta(days=1)
        
        completed_count = Stage.objects.filter(
            is_deleted=False,
            is_completed=True,
            completion_date__range=(day_start, day_end)
        ).count()
        
        last_7_days.append(day.strftime('%d.%m'))
        completed_by_day.append(completed_count)
    
    # ==================== ТОП-5 САМЫХ ЗАГРУЖЕННЫХ СТАНКОВ ====================
    top_loaded_machines = Machine.objects.filter(
        is_deleted=False
    ).select_related('model', 'workshop').order_by('-load_percent')[:5]
    
    # ==================== ПОСЛЕДНИЕ 10 ДЕТАЛЕЙ ====================
    recent_details = Detail.objects.filter(
        is_deleted=False
    ).select_related('status').order_by('-created_at')[:10]
    
    # ==================== СВОДНАЯ ТАБЛИЦА ДЕТАЛЕЙ С ПРОЦЕНТОМ ГОТОВНОСТИ ====================
    # Детали, отсортированные по проценту готовности (для таблицы)
    details_table = Detail.objects.filter(
        is_deleted=False
    ).select_related('status').prefetch_related(
        'stages'
    ).annotate(
        total_stages=Count('stages', filter=Q(stages__is_deleted=False)),
        completed_stages=Count('stages', filter=Q(stages__is_completed=True, stages__is_deleted=False))
    ).order_by('-completion_percent', 'planned_completion_date')[:15]
    
    # Добавляем информацию о текущем этапе для каждой детали
    for detail in details_table:
        detail.current_stage = detail.stages.filter(
            is_completed=False
        ).order_by('order_num').select_related('stage_type', 'machine').first()
    
    # ==================== СТАТУСЫ ПО ЦЕХАМ ====================
    workshop_status = []
    for workshop in workshops[:6]:  # Ограничим до 6 цехов для графика
        machines = workshop.machines.filter(is_deleted=False)
        workshop_status.append({
            'workshop': workshop.name,
            'active': machines.filter(status__name__icontains='работа').count(),
            'idle': machines.filter(status__name__icontains='ожида').count(),
            'maintenance': machines.filter(
                Q(status__name__icontains='ремонт') | 
                Q(status__name__icontains='неисправ')
            ).count(),
        })
    
    # ==================== ДЕТАЛИ С ВЫСОКИМ РИСКОМ ПРОСРОЧКИ ====================
    at_risk_details = Detail.objects.filter(
        is_deleted=False,
        planned_completion_date__lt=now + timedelta(days=3),
        planned_completion_date__gte=now,
        completion_percent__lt=70
    ).exclude(
        status__name__icontains='готов'
    ).select_related('status')[:5]
    
    context = {
        'now': now,
        'details_stats': details_stats,
        'machines_stats': machines_stats,
        'stages_stats': stages_stats,
        'machine_load_data': machine_load_data,
        'workshops_load': workshops_load,
        'last_7_days': last_7_days,
        'completed_by_day': completed_by_day,
        'top_loaded_machines': top_loaded_machines,
        'recent_details': recent_details,
        'details_table': details_table,
        'workshop_status': workshop_status,
        'at_risk_details': at_risk_details,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

def detail_list(request):
    """
    View для отображения списка деталей с использованием DataTables.
    """  
    completed_status = get_completed_status()  # Объект статуса завершенности
    now = timezone.now()  # Текущее время

   # Базовый queryset с оптимизацией запросов
    details = Detail.objects.select_related(
        'status'
    ).prefetch_related(
        'stages__stage_type',
        'stages__machine'
    ).filter(is_deleted=False)
    
    # Аннотируем дополнительную информацию
    details = details.annotate(
        total_stages=Count(
            'stages', 
            filter=Q(stages__is_deleted=False), 
            distinct=True
        ),
        completed_stages=Count(
            'stages', 
            filter=Q(stages__is_completed=True, 
                     stages__is_deleted=False)
        ),
        # current_stage_order=Coalesce(
        #     F('stages__order_num'),
        #     Value(0),
        #     output_field=IntegerField()
        # )
    )
    
    # Добавляем информацию о текущем этапе
    # for detail in details:
    #     detail.current_stage = detail.stages.filter(
    #         is_completed=False
    #     ).order_by('order_num').first()
    for detail in details:
        detail.current_stage = next(
            (
                stage
                for stage in detail.stages.all()
                if not stage.is_completed
            ),
            None
        )

        detail.is_completed = (detail.status == completed_status)

        detail.is_overdue = (
            detail.planned_completion_date
            and detail.planned_completion_date < now
            and not detail.is_completed
        )

        detail.is_warning = (
            detail.planned_completion_date
            and now <= detail.planned_completion_date <= now + timedelta(days=3)
            and not detail.is_completed
        )
        
    # Статистика для метрик
    total_details = details.count()
    completed_details = details.filter(status=completed_status).count()
    in_progress_details = details.filter(status__name__icontains='работе').count()
    
    # Просроченные детали   
    overdue_details = details.filter(
        planned_completion_date__lt=now
    ).exclude(
        status=completed_status
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



def stage_list(request):
    """
    View для отображения списка этапов обработки.
    """
    # Базовый queryset с оптимизацией запросов
    stages = Stage.objects.select_related(
        'detail',
        'stage_type',
        'machine',
        'machine__workshop',
        'machine__model'
    ).filter(
        is_deleted=False
    ).order_by(
        'detail_id', 
        'order_num'
    )
    
    # Аннотируем дополнительную информацию
    now = timezone.now()

    # Получаем все назначения для станков
    assignments = MachineAssignment.objects.filter(
        is_deleted=False
    ).select_related('detail', 'machine')
    
    # Создаем словарь для быстрого доступа к назначениям по этапам
    # Ключ: (machine_id, detail_id), значение: назначение
    assignments_dict = {}
    for assignment in assignments:
        key = (assignment.machine_id, assignment.detail_id)
        if key not in assignments_dict:  # Берем первое назначение
            assignments_dict[key] = assignment
    
    # Добавляем вычисляемые поля
    for stage in stages:
        # Проверка на просрочку
        if not stage.is_completed and stage.machine:
            # Ищем назначение для этого этапа
            # assignment = stage.machine.assignments.filter(
            #     detail=stage.detail,
            #     actual_end__isnull=True
            # ).first()
            assignment = assignments_dict.get((stage.machine_id, stage.detail_id))
            
            if assignment and assignment.planned_end < now:
                stage.is_overdue = True
            else:
                stage.is_overdue = False
        else:
            stage.is_overdue = False

        # Добавляем проверку на статус "В работе"
        if not stage.is_completed and stage.machine:
            stage.is_in_progress = stage.machine.assignments.filter(
                actual_start__isnull=False,
                actual_end__isnull=True,
                detail=stage.detail
            ).exists()
        else:
            stage.is_in_progress = False
        
        # Длительность выполнения
        if stage.completion_date and stage.created_at:
            duration = stage.completion_date - stage.created_at
            stage.duration_hours = round(duration.total_seconds() / 3600, 1)

    # Добавляем назначение к каждому этапу
    for stage in stages:
        key = (stage.machine_id, stage.detail_id)
        stage.related_assignment = assignments_dict.get(key)

    
    # Статистика для метрик
    total_stages = stages.count()
    completed_stages = stages.filter(is_completed=True).count()
    in_progress_stages = stages.filter(
        is_completed=False,
        machine__isnull=False,
        machine__assignments__actual_start__isnull=False,
        machine__assignments__actual_end__isnull=True
    ).distinct().count()
    pending_stages = stages.filter(
        is_completed=False,
        machine__isnull=True
    ).count()
    
    # Просроченные этапы
    overdue_stages = 0
    for stage in stages:
        if stage.is_overdue:
            overdue_stages += 1
    
    # Среднее время выполнения этапа   
    previous_stage_completion = Stage.objects.filter(
        detail=OuterRef('detail'),
        order_num__lt=OuterRef('order_num'),
        completion_date__isnull=False
    ).order_by('-order_num').values('completion_date')[:1]


    avg_duration = stages.filter(
        is_completed=True,
        completion_date__isnull=False
    ).annotate(
        prev_completion=Subquery(previous_stage_completion)
    ).filter(
        prev_completion__isnull=False
    ).annotate(
        duration=ExpressionWrapper(
            F('completion_date') - F('prev_completion'),
            output_field=DurationField()
        )
    ).aggregate(
        avg=Avg('duration')
    )['avg']


    if avg_duration:
        avg_hours = round(avg_duration.total_seconds() / 3600, 1)
    else:
        avg_hours = 0



    # avg_duration = stages.filter(
    #     is_completed=True,
    #     completion_date__isnull=False
    # ).annotate(
    #     duration=ExpressionWrapper(
    #         F('completion_date') - F('created_at'),
    #         output_field=DurationField()
    #     )
    # ).aggregate(avg=Avg('duration'))['avg']
    
    # if avg_duration:
    #     avg_hours = round(avg_duration.total_seconds() / 3600, 1)
    # else:
    #     avg_hours = 0
    
    # Получаем справочники для фильтров
    stage_types = StageType.objects.filter(
        stages__isnull=False
    ).distinct().order_by('name')
    
    machines = Machine.objects.filter(
        stages__isnull=False,
        is_deleted=False
    ).distinct().order_by('inventory_number')
    
    statuses = Status.objects.all()  # Для фильтра по статусу детали
    
    # Последние выполненные этапы
    recent_completed = stages.filter(
        is_completed=True,
        completion_date__isnull=False
    ).order_by('-completion_date')[:5]
    
    context = {
        'stages': stages,
        'total_stages': total_stages,
        'completed_stages': completed_stages,
        'in_progress_stages': in_progress_stages,
        'pending_stages': pending_stages,
        'overdue_stages': overdue_stages,
        'avg_duration': avg_hours,
        'stage_types': stage_types,
        'machines': machines,
        'statuses': statuses,
        'recent_completed': recent_completed,
        'now': now,
    }
    
    return render(request, 'stages/stage_list.html', context)




@login_required
def detail_detail(request, pk):
    """
    Возвращает данные детали в формате JSON для модального окна
    """
    detail = get_object_or_404(
        Detail.objects.select_related('status').prefetch_related(
            'stages__stage_type',
            'stages__machine__workshop'
        ),
        pk=pk,
        is_deleted=False
    )
    
    # Получаем все этапы детали
    stages = detail.stages.filter(is_deleted=False).order_by('order_num')
    
    # Получаем доступные станки для назначения
    available_machines = Machine.objects.filter(
        is_deleted=False
    ).select_related('model', 'workshop').order_by('inventory_number')
    
    # Получаем статусы для возможности смены статуса детали
    statuses = Status.objects.filter(
        Q(details__isnull=False) | Q(machines__isnull=False)
    ).distinct().order_by('name')
    
    # Формируем данные для JSON ответа
    data = {
        'id': detail.id,
        'article': detail.article,
        'name': detail.name,
        'drawing_number': detail.drawing_number or '',
        'planned_completion_date': detail.planned_completion_date.strftime('%Y-%m-%d %H:%M') if detail.planned_completion_date else '',
        'status': {
            'id': detail.status.id,
            'name': detail.status.name,
        },
        'completion_percent': float(detail.completion_percent),
        'description': detail.description or '',
        'created_at': detail.created_at.strftime('%d.%m.%Y %H:%M'),
        'updated_at': detail.updated_at.strftime('%d.%m.%Y %H:%M'),
        'stages': []
    }
    
    for stage in stages:
        stage_data = {
            'id': stage.id,
            'order_num': stage.order_num,
            'stage_type': {
                'id': stage.stage_type.id,
                'name': stage.stage_type.name,
            },
            'is_completed': stage.is_completed,
            'completion_date': stage.completion_date.strftime('%d.%m.%Y %H:%M') if stage.completion_date else None,
            'notes': stage.notes or '',
        }
        
        if stage.machine:
            stage_data['machine'] = {
                'id': stage.machine.id,
                'inventory_number': stage.machine.inventory_number,
                'model': stage.machine.model.name,
                'workshop': stage.machine.workshop.name,
                'load_percent': float(stage.machine.load_percent),
            }
        else:
            stage_data['machine'] = None
        
        # Проверка на просрочку
        if not stage.is_completed and stage.machine:
            assignment = stage.machine.assignments.filter(
                detail=detail,
                actual_end__isnull=True
            ).first()
            stage_data['is_overdue'] = bool(assignment and assignment.planned_end < timezone.now())
        else:
            stage_data['is_overdue'] = False
        
        data['stages'].append(stage_data)
    
    return JsonResponse(data)


@login_required
@require_POST
def detail_recalculate(request, pk):
    """
    Пересчитывает процент готовности детали
    """
    detail = get_object_or_404(Detail, pk=pk, is_deleted=False)
    detail.recalculate_completion()
    
    return JsonResponse({
        'success': True,
        'completion_percent': float(detail.completion_percent),
        'message': 'Процент готовности успешно пересчитан'
    })


@login_required
@require_POST
def stage_complete(request, pk, stage_id):
    """
    Отмечает этап как выполненный
    """
    stage = get_object_or_404(Stage, pk=stage_id, detail_id=pk, is_deleted=False)
    
    if not stage.is_completed:
        stage.is_completed = True
        stage.completion_date = timezone.now()
        stage.save()
        
        # Пересчитываем готовность детали
        stage.detail.recalculate_completion()
        
        return JsonResponse({
            'success': True,
            'message': 'Этап отмечен как выполненный',
            'completion_percent': float(stage.detail.completion_percent)
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Этап уже был выполнен ранее'
    })


@login_required
def detail_api(request, pk):
    """
    API для получения данных детали (альтернативный вариант)
    """
    return detail_detail(request, pk)


@login_required
@require_GET
def available_details_api(request):
    """
    Список деталей, которые ещё можно назначить на станки
    (без активного/текущего назначения или с незавершёнными этапами)
    """
    # Базовый вариант — все активные (не удалённые) детали
    # Можно ужесточить: без завершённых назначений, по цеху и т.д.
    completed_status = get_completed_status()
    details = Detail.objects.filter(
        is_deleted=False,
    ).exclude(
        status=completed_status
    ).order_by("article")

    data = [
        {
            "id": d.id,
            "article": d.article,
            "name": d.name or "(без названия)",
            "completion": float(d.completion_percent),  # для информации
            "status": d.status.name if d.status else "—",
        }
        for d in details
    ]

    return JsonResponse(data, safe=False)


@login_required
@require_GET
def detail_stages_api(request, detail_id):
    """
    Возвращает этапы конкретной детали (Stage), которые ещё не завершены
    """
    try:
        detail = Detail.objects.get(pk=detail_id, is_deleted=False)
    except Detail.DoesNotExist:
        return JsonResponse({"error": "Деталь не найдена"}, status=404)

    stages = Stage.objects.filter(
        detail=detail,
        is_deleted=False,
        is_completed=False
    ).select_related("stage_type", "machine").order_by("order_num")

    data = [
        {
            "id": stage.id,
            "order": stage.order_num,
            "name": stage.stage_type.name,
            "machine": stage.machine.__str__() if stage.machine else "Не назначен",
            "machine_id": stage.machine.id if stage.machine else None,
        }
        for stage in stages
    ]

    return JsonResponse(data, safe=False)


@require_POST
@login_required  
def assign_task_to_machine(request, machine_id):
    """
    Назначает задачу (этап детали) на конкретный станок.
    
    Ожидаемые поля в POST:
    - detail       (id детали)
    - stage        (id этапа Stage)
    - planned_start (datetime-local строка)
    - planned_end   (datetime-local строка)
    - notes         (опционально)
    """
    machine = get_object_or_404(Machine, pk=machine_id, is_deleted=False)

    detail_id = request.POST.get('detail')
    stage_id  = request.POST.get('stage')
    start_str = request.POST.get('planned_start')
    end_str   = request.POST.get('planned_end')
    notes     = request.POST.get('notes', '').strip()

    if not all([detail_id, stage_id, start_str, end_str]):
        return JsonResponse({
            "success": False,
            "error": "Не переданы все обязательные поля"
        }, status=400)

    try:
        detail = Detail.objects.get(pk=detail_id, is_deleted=False)
        stage  = Stage.objects.get(
            pk=stage_id,
            detail=detail,           # защита: этап должен принадлежать этой детали
            is_deleted=False,
            is_completed=False       # нельзя назначать уже завершённый этап
        )
    except (Detail.DoesNotExist, Stage.DoesNotExist):
        return JsonResponse({
            "success": False,
            "error": "Деталь или этап не найдены / недоступны"
        }, status=404)

    # Парсим даты (формат datetime-local → 2025-03-13T14:30)
    try:
        planned_start = timezone.datetime.fromisoformat(start_str)
        planned_end   = timezone.datetime.fromisoformat(end_str)

        if planned_end <= planned_start:
            return JsonResponse({
                "success": False,
                "error": "Дата окончания должна быть позже даты начала"
            }, status=400)

    except ValueError:
        return JsonResponse({
            "success": False,
            "error": "Некорректный формат дат"
        }, status=400)

    # Проверяем, не занят ли станок в это время (очень базовая проверка)
    overlapping = MachineAssignment.objects.filter(
        machine=machine,
        planned_start__lt=planned_end,
        planned_end__gt=planned_start,
        # можно добавить: actual_end__isnull=True  — только активные
    ).exists()

    if overlapping:
        return JsonResponse({
            "success": False,
            "error": "Станок уже имеет назначение в этот временной интервал"
        }, status=409)  # Conflict

    # Создаём назначение
    assignment = MachineAssignment.objects.create(
        machine=machine,
        detail=detail,
        planned_start=planned_start,
        planned_end=planned_end,
        notes=notes,
        # created_by=request.user  — если добавишь поле в модель
    )

    # Можно связать этап с назначением, если добавишь ForeignKey в Stage → assignment
    # stage.assignment = assignment
    # stage.save(update_fields=['assignment'])

    # Опционально: изменить статус станка, если он был в ожидании
    if machine.status and "ожида" in machine.status.name.lower():
        working_status = Status.objects.filter(name__icontains="работа").first()
        if working_status:
            machine.status = working_status
            machine.save(update_fields=['status'])

    return JsonResponse({
        "success": True,
        "assignment_id": assignment.id,
        "message": f"Этап {stage} детали {detail} назначен на {machine}"
    })