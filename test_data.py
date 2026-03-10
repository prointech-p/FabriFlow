from django.db import IntegrityError
from apps.core.models import Status, StageType, MachineModel, Workshop

print("Начинаем заполнение справочников...\n")

# ==================== ЗАПОЛНЕНИЕ СТАТУСОВ (Status) ====================
print("--- Заполнение статусов ---")
statuses = [
    {"name": "В работе", "description": "Деталь или станок в процессе обработки"},
    {"name": "Заморожено", "description": "Работы приостановлены по различным причинам"},
    {"name": "Завершено", "description": "Работы успешно завершены"},
    {"name": "Отменено", "description": "Работы отменены"},
    {"name": "Ожидает материалов", "description": "Ожидание поступления материалов для начала работ"},
]

for data in statuses:
    try:
        obj, created = Status.objects.get_or_create(
            name=data["name"],
            defaults={"description": data["description"]}
        )
        if created:
            print(f"✓ Создан статус: '{data['name']}'")
        else:
            print(f"→ Статус уже существует: '{data['name']}'")
    except IntegrityError as e:
        print(f"✗ Ошибка при создании статуса '{data['name']}': {e}")

print(f"Всего статусов в базе: {Status.objects.count()}\n")


# ==================== ЗАПОЛНЕНИЕ ТИПОВ ЭТАПОВ (StageType) ====================
print("--- Заполнение типов этапов ---")
stage_types = [
    {"name": "Токарная обработка", "description": "Обработка на токарном станке"},
    {"name": "Фрезеровка", "description": "Фрезерная обработка детали"},
    {"name": "Сверление", "description": "Сверление отверстий"},
    {"name": "Шлифовка", "description": "Финишная шлифовка поверхностей"},
    {"name": "Термическая обработка", "description": "Термообработка для изменения свойств материала"},
    {"name": "Контроль качества", "description": "Проверка соответствия требованиям"},
]

for data in stage_types:
    try:
        obj, created = StageType.objects.get_or_create(
            name=data["name"],
            defaults={"description": data["description"]}
        )
        if created:
            print(f"✓ Создан тип этапа: '{data['name']}'")
        else:
            print(f"→ Тип этапа уже существует: '{data['name']}'")
    except IntegrityError as e:
        print(f"✗ Ошибка при создании типа этапа '{data['name']}': {e}")

print(f"Всего типов этапов в базе: {StageType.objects.count()}\n")


# ==================== ЗАПОЛНЕНИЕ МОДЕЛЕЙ СТАНКОВ (MachineModel) ====================
print("--- Заполнение моделей станков ---")
machine_models = [
    {"name": "16К20", "manufacturer": "Красный пролетарий", "description": "Универсальный токарно-винторезный станок"},
    {"name": "6Р82Ш", "manufacturer": "Горьковский завод фрезерных станков", "description": "Широкоуниверсальный фрезерный станок"},
    {"name": "2Н135", "manufacturer": "Стерлитамакский станкостроительный завод", "description": "Вертикально-сверлильный станок"},
    {"name": "3Г71", "manufacturer": "Московский завод шлифовальных станков", "description": "Плоскошлифовальный станок"},
    {"name": "ТВ-7", "manufacturer": "Тульский станкостроительный завод", "description": "Токарно-винторезный станок учебный"},
]

for data in machine_models:
    try:
        obj, created = MachineModel.objects.get_or_create(
            name=data["name"],
            defaults={
                "manufacturer": data["manufacturer"],
                "description": data["description"]
            }
        )
        if created:
            print(f"✓ Создана модель станка: '{data['name']}' ({data['manufacturer']})")
        else:
            print(f"→ Модель станка уже существует: '{data['name']}'")
    except IntegrityError as e:
        print(f"✗ Ошибка при создании модели станка '{data['name']}': {e}")

print(f"Всего моделей станков в базе: {MachineModel.objects.count()}\n")


# ==================== ЗАПОЛНЕНИЕ ЦЕХОВ (Workshop) ====================
print("--- Заполнение цехов ---")
workshops = [
    {"name": "Механический цех №1", "code": "МЦ-01", "description": "Цех механической обработки, специализация - токарные и фрезерные работы"},
    {"name": "Механический цех №2", "code": "МЦ-02", "description": "Цех механической обработки, специализация - сверлильные и расточные работы"},
    {"name": "Механосборочный цех", "code": "СЦ-01", "description": "Цех сборки готовых изделий"},
    {"name": "Термический цех", "code": "ТЦ-01", "description": "Цех термической обработки деталей"},
    {"name": "Инструментальный цех", "code": "ИЦ-01", "description": "Цех изготовления и ремонта инструмента"},
    {"name": "Цех ЧПУ", "code": "ЧПУ-01", "description": "Цех станков с ЧПУ"},
]

for data in workshops:
    try:
        obj, created = Workshop.objects.get_or_create(
            name=data["name"],
            defaults={
                "code": data["code"],
                "description": data["description"]
            }
        )
        if created:
            print(f"✓ Создан цех: '{data['name']}' ({data['code']})")
        else:
            print(f"→ Цех уже существует: '{data['name']}'")
    except IntegrityError as e:
        print(f"✗ Ошибка при создании цеха '{data['name']}': {e}")

print(f"Всего цехов в базе: {Workshop.objects.count()}\n")

print("=" * 50)
print("ЗАПОЛНЕНИЕ СПРАВОЧНИКОВ ЗАВЕРШЕНО")
print("=" * 50)

# Вывод итоговой статистики
print(f"\nИтоговая статистика:")
print(f"Статусы: {Status.objects.count()} записей")
print(f"Типы этапов: {StageType.objects.count()} записей")
print(f"Модели станков: {MachineModel.objects.count()} записей")
print(f"Цеха: {Workshop.objects.count()} записей")


from datetime import datetime
from decimal import Decimal
from apps.core.models import Detail, Status

print("Начинаем заполнение деталей...\n")

# Получаем все статусы для удобства работы
statuses = {s.id: s for s in Status.objects.all()}

# Проверяем наличие всех необходимых статусов
required_status_ids = [1, 3, 4]
for status_id in required_status_ids:
    if status_id not in statuses:
        print(f"✗ Внимание: Статус с ID {status_id} не найден в базе!")
        print("  Убедитесь, что сначала запущен скрипт заполнения справочников.")
        exit(1)

print(f"✓ Найдены все необходимые статусы\n")

# Данные деталей
details_data = [
    {
        "article": "DTL-001",
        "name": "Вал приводной",
        "drawing_number": "DRW-1001-01",
        "planned_completion_date": datetime(2026, 4, 15, 17, 0),  # 2026-04-15 17:00:00
        "status": statuses[1],  # "В работе"
        "completion_percent": Decimal("65.5"),
        "description": "Приводной вал для редуктора, сталь 40Х, термообработка"
    },
    {
        "article": "DTL-002",
        "name": "Фланец соединительный",
        "drawing_number": "DRW-1002-03",
        "planned_completion_date": datetime(2026, 3, 20, 16, 0),  # 2026-03-20 16:00:00
        "status": statuses[1],  # "В работе"
        "completion_percent": Decimal("100.0"),
        "description": "Фланец для соединения валов, материал - сталь 45"
    },
    {
        "article": "DTL-003",
        "name": "Корпус редуктора",
        "drawing_number": "DRW-1003-07",
        "planned_completion_date": datetime(2025, 12, 22, 18, 0),  # 2025-12-22 18:00:00
        "status": statuses[3],  # "Завершено"
        "completion_percent": Decimal("40.25"),
        "description": "Корпус двухступенчатого редуктора, чугун СЧ20"
    },
    {
        "article": "DTL-004",
        "name": "Ось направляющая",
        "drawing_number": "DRW-1004-02",
        "planned_completion_date": datetime(2024, 1, 10, 15, 0),  # 2024-01-10 15:00:00
        "status": statuses[4],  # "Отменено"
        "completion_percent": Decimal("80.75"),
        "description": "Направляющая ось для линейных перемещений"
    },
]

# Создаем детали
created_count = 0
updated_count = 0

for data in details_data:
    try:
        obj, created = Detail.objects.update_or_create(
            article=data["article"],  # Уникальное поле для поиска
            defaults={
                "name": data["name"],
                "drawing_number": data["drawing_number"],
                "planned_completion_date": data["planned_completion_date"],
                "status": data["status"],
                "completion_percent": data["completion_percent"],
                "description": data.get("description", ""),
            }
        )
        
        if created:
            created_count += 1
            print(f"✓ Создана деталь: {obj.article} — {obj.name}")
        else:
            updated_count += 1
            print(f"↻ Обновлена деталь: {obj.article} — {obj.name}")
            
        # Дополнительная информация о детали
        print(f"  • Чертеж: {obj.drawing_number}")
        print(f"  • Статус: {obj.status.name} (ID: {obj.status.id})")
        print(f"  • Готовность: {obj.completion_percent}%")
        print(f"  • Плановая дата: {obj.planned_completion_date.strftime('%d.%m.%Y %H:%M')}")
        print()
        
    except Exception as e:
        print(f"✗ Ошибка при создании/обновлении {data['article']}: {e}")
        print()

print("=" * 50)
print(f"ИТОГИ ЗАПОЛНЕНИЯ ДЕТАЛЕЙ:")
print(f"Создано новых: {created_count}")
print(f"Обновлено существующих: {updated_count}")
print(f"Всего деталей в базе: {Detail.objects.count()}")
print("=" * 50)

# Дополнительная статистика по статусам
print(f"\nСтатистика по статусам:")
for status_id in [1, 3, 4]:
    status = statuses[status_id]
    count = Detail.objects.filter(status=status).count()
    print(f"• {status.name}: {count} дет.")







from decimal import Decimal
from datetime import datetime
from apps.core.models import Machine, MachineModel, Workshop, Status

print("Начинаем заполнение станков...\n")

# Получаем все справочники
models = {m.id: m for m in MachineModel.objects.all()}
workshops = {w.id: w for w in Workshop.objects.all()}
statuses = {s.id: s for s in Status.objects.all()}

# Данные станков
machines_data = [
    {
        "id": 1,
        "inventory_number": "СТ-16К20-001",
        "model": models[1],
        "workshop": workshops[1],
        "status": statuses[1],
        "load_percent": Decimal("75.5"),
        "commissioning_date": datetime(2023, 5, 15).date(),
    },
    {
        "id": 2,
        "inventory_number": "СТ-6Р82Ш-001",
        "model": models[2],
        "workshop": workshops[1],
        "status": statuses[1],
        "load_percent": Decimal("82.3"),
        "commissioning_date": datetime(2022, 3, 10).date(),
    },
    {
        "id": 3,
        "inventory_number": "СТ-2Н135-001",
        "model": models[3],
        "workshop": workshops[2],
        "status": statuses[2],
        "load_percent": Decimal("0.0"),
        "commissioning_date": datetime(2021, 11, 20).date(),
    },
    {
        "id": 4,
        "inventory_number": "СТ-3Г71-001",
        "model": models[4],
        "workshop": workshops[3],
        "status": statuses[1],
        "load_percent": Decimal("45.0"),
        "commissioning_date": datetime(2024, 1, 15).date(),
    },
    {
        "id": 5,
        "inventory_number": "СТ-ТВ7-001",
        "model": models[5],
        "workshop": workshops[5],
        "status": statuses[1],
        "load_percent": Decimal("35.8"),
        "commissioning_date": datetime(2023, 8, 5).date(),
    },
]

# Создаем станки
created_count = 0
updated_count = 0

for data in machines_data:
    try:
        inventory_number = data["inventory_number"]
        
        obj, created = Machine.objects.update_or_create(
            inventory_number=inventory_number,
            defaults={
                "model": data["model"],
                "workshop": data["workshop"],
                "status": data["status"],
                "load_percent": data["load_percent"],
                "commissioning_date": data["commissioning_date"],
            }
        )
        
        if created:
            created_count += 1
            print(f"✓ Создан станок: {obj.inventory_number}")
        else:
            updated_count += 1
            print(f"↻ Обновлен станок: {obj.inventory_number}")
        
        print(f"  • Модель: {obj.model.name}")
        print(f"  • Цех: {obj.workshop.name}")
        print(f"  • Статус: {obj.status.name}")
        print(f"  • Загрузка: {obj.load_percent}%")
        print()
        
    except Exception as e:
        print(f"✗ Ошибка при создании станка {data['inventory_number']}: {e}")
        print()

print(f"ИТОГИ: Создано {created_count}, обновлено {updated_count}")
print(f"Всего станков: {Machine.objects.count()}")



from datetime import datetime
from apps.core.models import Stage, Detail, StageType, Machine

print("Начинаем заполнение этапов обработки...\n")

# Получаем все необходимые справочники
details = {d.article: d for d in Detail.objects.all()}  # Индексируем по article
stage_types = {st.id: st for st in StageType.objects.all()}
machines = {m.id: m for m in Machine.objects.all()}

# Для удобства также создаем словарь деталей по ID (для поиска)
details_by_id = {d.id: d for d in Detail.objects.all()}

print("Проверка наличия справочных данных:")

# Проверка деталей
required_detail_ids = [1, 2, 3, 4]
for detail_id in required_detail_ids:
    detail = details_by_id.get(detail_id)
    if detail:
        print(f"  ✓ Деталь ID {detail_id}: {detail.article} — {detail.name}")
    else:
        print(f"  ✗ Деталь ID {detail_id} не найдена!")

# Проверка типов этапов
required_stage_ids = [1, 2, 4, 6]
for stage_id in required_stage_ids:
    if stage_id in stage_types:
        print(f"  ✓ Тип этапа ID {stage_id}: {stage_types[stage_id].name}")
    else:
        print(f"  ✗ Тип этапа ID {stage_id} не найден!")

# Проверка станков
required_machine_ids = [1, 2, 4]
for machine_id in required_machine_ids:
    if machine_id in machines:
        print(f"  ✓ Станок ID {machine_id}: {machines[machine_id].inventory_number}")
    else:
        print(f"  ✗ Станок ID {machine_id} не найден!")

print("\n" + "=" * 60)

# Данные этапов обработки
stages_data = [
    # DTL-001 (Вал приводной) - в работе
    {
        "detail": details_by_id[1],  # DTL-001
        "stage_type": stage_types[1],  # Токарная обработка
        "order_num": 1,
        "machine": machines.get(1),  # СТ-16К20-001
        "is_completed": False,
        "completion_date": None,
        "notes": "Токарная обработка вала, черновой проход"
    },
    {
        "detail": details_by_id[1],  # DTL-001
        "stage_type": stage_types[2],  # Фрезеровка
        "order_num": 2,
        "machine": machines.get(2),  # СТ-6Р82Ш-001
        "is_completed": False,
        "completion_date": None,
        "notes": "Фрезеровка шпоночного паза"
    },
    {
        "detail": details_by_id[1],  # DTL-001
        "stage_type": stage_types[4],  # Шлифовка
        "order_num": 3,
        "machine": machines.get(4),  # СТ-3Г71-001
        "is_completed": False,
        "completion_date": None,
        "notes": "Финишная шлифовка поверхности"
    },
    
    # DTL-002 (Фланец соединительный) - частично завершен
    {
        "detail": details_by_id[2],  # DTL-002
        "stage_type": stage_types[1],  # Токарная обработка
        "order_num": 1,
        "machine": machines.get(1),  # СТ-16К20-001
        "is_completed": True,
        "completion_date": datetime(2026, 2, 15, 17, 20),
        "notes": "Токарная обработка фланца, выполнена в срок"
    },
    {
        "detail": details_by_id[2],  # DTL-002
        "stage_type": stage_types[2],  # Фрезеровка
        "order_num": 2,
        "machine": machines.get(2),  # СТ-6Р82Ш-001
        "is_completed": True,
        "completion_date": datetime(2026, 3, 16, 10, 15),
        "notes": "Фрезеровка отверстий под крепление"
    },
    {
        "detail": details_by_id[2],  # DTL-002
        "stage_type": stage_types[6],  # Контроль качества
        "order_num": 3,
        "machine": None,  # Станок не указан (контроль ОТК)
        "is_completed": False,
        "completion_date": None,
        "notes": "Контроль качества после мехобработки"
    },
    
    # DTL-003 (Корпус редуктора) - полностью завершен
    {
        "detail": details_by_id[3],  # DTL-003
        "stage_type": stage_types[1],  # Токарная обработка
        "order_num": 1,
        "machine": machines.get(1),  # СТ-16К20-001
        "is_completed": True,
        "completion_date": datetime(2025, 12, 5, 13, 10),
        "notes": "Токарная обработка посадочных мест"
    },
    {
        "detail": details_by_id[3],  # DTL-003
        "stage_type": stage_types[2],  # Фрезеровка
        "order_num": 2,
        "machine": machines.get(2),  # СТ-6Р82Ш-001
        "is_completed": True,
        "completion_date": datetime(2025, 12, 22, 13, 10, 1),
        "notes": "Фрезеровка плоскостей разъема"
    },
    
    # DTL-004 (Ось направляющая) - завершен (но деталь отменена)
    {
        "detail": details_by_id[4],  # DTL-004
        "stage_type": stage_types[1],  # Токарная обработка
        "order_num": 1,
        "machine": machines.get(1),  # СТ-16К20-001
        "is_completed": True,
        "completion_date": datetime(2024, 11, 5, 13, 10, 2),
        "notes": "Токарная обработка оси, выполнена полностью"
    },
]

# Создаем этапы
created_count = 0
updated_count = 0

for data in stages_data:
    try:
        # Для этапов уникальность определяется деталью + номером этапа
        obj, created = Stage.objects.update_or_create(
            detail=data["detail"],
            order_num=data["order_num"],
            defaults={
                "stage_type": data["stage_type"],
                "machine": data["machine"],
                "is_completed": data["is_completed"],
                "completion_date": data["completion_date"],
                "notes": data.get("notes", ""),
            }
        )
        
        if created:
            created_count += 1
            status_icon = "✓"
        else:
            updated_count += 1
            status_icon = "↻"
        
        # Формируем строку статуса выполнения
        completion_status = "ЗАВЕРШЕН" if obj.is_completed else "В РАБОТЕ"
        if obj.completion_date:
            completion_status += f" ({obj.completion_date.strftime('%d.%m.%Y %H:%M')})"
        
        machine_info = obj.machine.inventory_number if obj.machine else "ОТК/Контроль"
        
        print(f"{status_icon} Этап {obj.order_num} для {obj.detail.article}")
        print(f"  • Тип: {obj.stage_type.name}")
        print(f"  • Станок: {machine_info}")
        print(f"  • Статус: {completion_status}")
        print()
        
    except Exception as e:
        print(f"✗ Ошибка при создании этапа для детали {data['detail'].article}, порядок {data['order_num']}: {e}")
        print()

print("=" * 60)
print(f"ИТОГИ ЗАПОЛНЕНИЯ ЭТАПОВ:")
print(f"Создано новых: {created_count}")
print(f"Обновлено существующих: {updated_count}")
print(f"Всего этапов в базе: {Stage.objects.count()}")
print("=" * 60)

# Статистика по деталям
print(f"\nСтатистика по деталям:")
for detail_id in [1, 2, 3, 4]:
    detail = details_by_id.get(detail_id)
    if detail:
        stages_count = Stage.objects.filter(detail=detail).count()
        completed_count = Stage.objects.filter(detail=detail, is_completed=True).count()
        print(f"• {detail.article} ({detail.name}): {stages_count} этапов, выполнено {completed_count}")




from datetime import datetime
from apps.core.models import MachineAssignment, Machine, Detail

print("Начинаем заполнение назначений деталей на станки...\n")

# Получаем все необходимые справочники
machines = {m.id: m for m in Machine.objects.all()}
details = {d.id: d for d in Detail.objects.all()}
details_by_article = {d.article: d for d in Detail.objects.all()}

print("Проверка наличия справочных данных:")

# Проверка станков
required_machine_ids = [1, 2, 4]
for machine_id in required_machine_ids:
    if machine_id in machines:
        print(f"  ✓ Станок ID {machine_id}: {machines[machine_id].inventory_number} ({machines[machine_id].model.name})")
    else:
        print(f"  ✗ Станок ID {machine_id} не найден!")

# Проверка деталей
required_detail_ids = [1, 2]
for detail_id in required_detail_ids:
    if detail_id in details:
        print(f"  ✓ Деталь ID {detail_id}: {details[detail_id].article} — {details[detail_id].name}")
    else:
        print(f"  ✗ Деталь ID {detail_id} не найдена!")

print("\n" + "=" * 60)

# Данные назначений
assignments_data = [
    # Назначение 1: СТ-16К20-001 (id=1) -> DTL-001 (Вал приводной)
    {
        "id": 1,
        "machine": machines[1],  # СТ-16К20-001
        "detail": details[1],     # DTL-001
        "assignment_date": None,
        "planned_start": datetime(2026, 3, 11, 8, 0, 0),   # 2026-03-11 08:00:00
        "actual_start": None,
        "planned_end": datetime(2026, 3, 15, 8, 0, 0),     # 2026-03-15 08:00:00
        "actual_end": None,
        "notes": "Токарная обработка вала приводного DTL-001"
    },
    
    # Назначение 2: СТ-6Р82Ш-001 (id=2) -> DTL-001 (Вал приводной)
    {
        "id": 2,
        "machine": machines[2],  # СТ-6Р82Ш-001
        "detail": details[1],     # DTL-001
        "assignment_date": None,
        "planned_start": datetime(2026, 3, 16, 8, 0, 0),   # 2026-03-16 08:00:00
        "actual_start": None,
        "planned_end": datetime(2026, 3, 16, 8, 0, 0),     # 2026-03-16 08:00:00 (в тот же день?)
        "actual_end": None,
        "notes": "Фрезеровка шпоночного паза на валу DTL-001"
    },
    
    # Назначение 3: СТ-3Г71-001 (id=4) -> DTL-001 (Вал приводной)
    {
        "id": 3,
        "machine": machines[4],  # СТ-3Г71-001
        "detail": details[1],     # DTL-001
        "assignment_date": None,
        "planned_start": datetime(2026, 4, 2, 8, 0, 0),    # 2026-04-02 08:00:00
        "actual_start": None,
        "planned_end": datetime(2026, 4, 7, 8, 0, 0),      # 2026-04-07 08:00:00
        "actual_end": None,
        "notes": "Финишная шлифовка вала DTL-001"
    },
    
    # Назначение 4: СТ-6Р82Ш-001 (id=2) -> DTL-002 (Фланец соединительный)
    {
        "id": 4,
        "machine": machines[2],  # СТ-6Р82Ш-001
        "detail": details[2],     # DTL-002
        "assignment_date": datetime(2026, 3, 14, 10, 15, 0),  # 2026-03-14 10:15:00
        "planned_start": datetime(2026, 3, 14, 8, 0, 0),      # 2026-03-14 08:00:00
        "actual_start": datetime(2026, 3, 14, 10, 15, 0),     # 2026-03-14 10:15:00
        "planned_end": datetime(2026, 3, 17, 18, 10, 0),      # 2026-03-17 18:10:00
        "actual_end": None,  # Не указано, предположительно еще не завершено
        "notes": "Фрезеровка отверстий во фланце DTL-002 (начато с опозданием)"
    },
]

# Создаем назначения
created_count = 0
updated_count = 0

for data in assignments_data:
    try:
        # Для назначений используем комбинацию станок + деталь + planned_start как уникальный идентификатор
        obj, created = MachineAssignment.objects.update_or_create(
            machine=data["machine"],
            detail=data["detail"],
            planned_start=data["planned_start"],
            defaults={
                "assignment_date": data.get("assignment_date"),
                "actual_start": data.get("actual_start"),
                "planned_end": data["planned_end"],
                "actual_end": data.get("actual_end"),
                "notes": data.get("notes", ""),
            }
        )
        
        if created:
            created_count += 1
            status_icon = "✓"
            action = "Создано"
        else:
            updated_count += 1
            status_icon = "↻"
            action = "Обновлено"
        
        # Формируем информацию о статусе выполнения
        start_info = "не начато"
        if obj.actual_start:
            if obj.actual_end:
                start_info = f"завершено {obj.actual_end.strftime('%d.%m.%Y %H:%M')}"
            else:
                start_info = f"в работе с {obj.actual_start.strftime('%d.%m.%Y %H:%M')}"
        
        # Информация о дате назначения
        assignment_info = ""
        if obj.assignment_date:
            assignment_info = f" (назначено {obj.assignment_date.strftime('%d.%m.%Y %H:%M')})"
        
        print(f"{status_icon} {action} назначение #{data['id']}")
        print(f"  • Станок: {obj.machine.inventory_number} ({obj.machine.model.name})")
        print(f"  • Деталь: {obj.detail.article} — {obj.detail.name}")
        print(f"  • План: {obj.planned_start.strftime('%d.%m.%Y %H:%M')} - {obj.planned_end.strftime('%d.%m.%Y %H:%M')}")
        print(f"  • Статус: {start_info}{assignment_info}")
        print()
        
    except Exception as e:
        print(f"✗ Ошибка при создании назначения #{data['id']}: {e}")
        print()

print("=" * 60)
print(f"ИТОГИ ЗАПОЛНЕНИЯ НАЗНАЧЕНИЙ:")
print(f"Создано новых: {created_count}")
print(f"Обновлено существующих: {updated_count}")
print(f"Всего назначений в базе: {MachineAssignment.objects.count()}")
print("=" * 60)

# Статистика по станкам
print(f"\nСтатистика по станкам:")
for machine_id in [1, 2, 4]:
    if machine_id in machines:
        machine = machines[machine_id]
        assignments_count = MachineAssignment.objects.filter(machine=machine).count()
        active_assignments = MachineAssignment.objects.filter(
            machine=machine, 
            actual_start__isnull=False,
            actual_end__isnull=True
        ).count()
        print(f"• {machine.inventory_number}: {assignments_count} назначений, {active_assignments} в работе")

# Статистика по деталям
print(f"\nСтатистика по деталям:")
for detail_id in [1, 2]:
    if detail_id in details:
        detail = details[detail_id]
        assignments_count = MachineAssignment.objects.filter(detail=detail).count()
        print(f"• {detail.article}: {assignments_count} назначений")