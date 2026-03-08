from django.db import IntegrityError
from apps.core.models import Status, StageType, MachineModel, Workshop  # Замените 'app' на имя вашего приложения, где находятся модели

# Заполнение статусов (Status)
statuses = [
    {"name": "Ожидание", "description": "Объект ожидает начала работ или ресурсов"},
    {"name": "В производстве", "description": "Объект активно обрабатывается"},
    {"name": "Завершено", "description": "Работы по объекту завершены успешно"},
    {"name": "Отменено", "description": "Работы отменены по какой-либо причине"},
    {"name": "Неисправен", "description": "Станок требует ремонта"},
    {"name": "На обслуживании", "description": "Станок на плановом ТО"},
]

for data in statuses:
    try:
        Status.objects.get_or_create(name=data["name"], defaults={"description": data["description"]})
        print(f"Статус '{data['name']}' создан или уже существует.")
    except IntegrityError:
        print(f"Ошибка при создании статуса '{data['name']}'.")

# Заполнение типов этапов (StageType)
stage_types = [
    {"name": "Резка заготовки", "description": "Первичная резка материала для получения заготовки"},
    {"name": "Токарная обработка", "description": "Обработка на токарном станке для придания формы"},
    {"name": "Фрезеровка", "description": "Фрезерная обработка для создания пазов и поверхностей"},
    {"name": "Сверление", "description": "Создание отверстий с помощью сверлильного оборудования"},
    {"name": "Шлифовка", "description": "Финишная шлифовка для достижения точности и гладкости"},
    {"name": "Термообработка", "description": "Термическая обработка для изменения свойств материала"},
    {"name": "Сборка", "description": "Сборка компонентов детали, если требуется"},
    {"name": "Контроль качества", "description": "Проверка размеров и качества на соответствие чертежу"},
]

for data in stage_types:
    try:
        StageType.objects.get_or_create(name=data["name"], defaults={"description": data["description"]})
        print(f"Тип этапа '{data['name']}' создан или уже существует.")
    except IntegrityError:
        print(f"Ошибка при создании типа этапа '{data['name']}'.")

# Заполнение моделей станков (MachineModel)
machine_models = [
    {"name": "Haas VF-2", "manufacturer": "Haas Automation", "description": "Вертикальный фрезерный центр с ЧПУ, 3 оси, высокая точность"},
    {"name": "DMG MORI CMX 1100 V", "manufacturer": "DMG MORI", "description": "Вертикальный обрабатывающий центр, 4 оси, для средних деталей"},
    {"name": "Mazak VTC-200C", "manufacturer": "Yamazaki Mazak", "description": "Вертикальный фрезерный станок с ЧПУ, большая рабочая зона"},
    {"name": "Okuma GENOS M560-V", "manufacturer": "Okuma", "description": "Фрезерный центр с высокой жесткостью, для тяжелых работ"},
    {"name": "Doosan DNM 5700", "manufacturer": "Doosan", "description": "Вертикальный фрезерный станок, экономичный вариант для серийного производства"},
    {"name": "Fanuc Robodrill", "manufacturer": "Fanuc", "description": "Компактный сверлильно-фрезерный центр с высокой скоростью"},
]

for data in machine_models:
    try:
        MachineModel.objects.get_or_create(
            name=data["name"],
            defaults={"manufacturer": data["manufacturer"], "description": data["description"]}
        )
        print(f"Модель станка '{data['name']}' создана или уже существует.")
    except IntegrityError:
        print(f"Ошибка при создании модели станка '{data['name']}'.")

# Заполнение цехов (Workshop)
workshops = [
    {"name": "Механический цех №1", "code": "МЦ-01", "description": "Основной цех для механообработки, начальник: Иванов И.И., площадь 500 м²"},
    {"name": "Токарный цех", "code": "ТЦ-02", "description": "Специализированный цех для токарных работ, оборудован 10 станками"},
    {"name": "Сборочный цех", "code": "СЦ-03", "description": "Цех для финальной сборки и контроля, с зоной тестирования"},
]

for data in workshops:
    try:
        Workshop.objects.get_or_create(
            name=data["name"],
            defaults={"code": data["code"], "description": data["description"]}
        )
        print(f"Цех '{data['name']}' создан или уже существует.")
    except IntegrityError:
        print(f"Ошибка при создании цеха '{data['name']}'.")


from datetime import datetime
from decimal import Decimal
from apps.core.models import Machine, MachineModel, Workshop, Status  

# Предварительно получаем объекты справочников (по name — самый надёжный способ)
models_dict = {m.name: m for m in MachineModel.objects.all()}
workshops_dict = {w.name: w for w in Workshop.objects.all()}
statuses_dict = {s.name: s for s in Status.objects.all()}

# Данные станков
machines_data = [
    {
        "inventory_number": "СТ-001",
        "model": models_dict["Haas VF-2"],
        "workshop": workshops_dict["Механический цех №1"],
        "status": statuses_dict["В производстве"],
        "load_percent": Decimal("78.50"),
        "commissioning_date": datetime(2023, 5, 15).date(),
    },
    {
        "inventory_number": "СТ-002",
        "model": models_dict["Haas VF-2"],
        "workshop": workshops_dict["Механический цех №1"],
        "status": statuses_dict["В производстве"],
        "load_percent": Decimal("92.00"),
        "commissioning_date": datetime(2024, 2, 10).date(),
    },
    {
        "inventory_number": "СТ-005",
        "model": models_dict["DMG MORI CMX 1100 V"],
        "workshop": workshops_dict["Механический цех №1"],
        "status": statuses_dict["Ожидание"],
        "load_percent": Decimal("12.30"),
        "commissioning_date": datetime(2022, 11, 20).date(),
    },
    {
        "inventory_number": "СТ-008",
        "model": models_dict["Mazak VTC-200C"],
        "workshop": workshops_dict["Механический цех №1"],
        "status": statuses_dict["На обслуживании"],
        "load_percent": Decimal("0.00"),
        "commissioning_date": datetime(2021, 8, 5).date(),
    },
    {
        "inventory_number": "СТ-010",
        "model": models_dict["Okuma GENOS M560-V"],
        "workshop": workshops_dict["Токарный цех"],
        "status": statuses_dict["В производстве"],
        "load_percent": Decimal("65.40"),
        "commissioning_date": datetime(2023, 9, 12).date(),
    },
    {
        "inventory_number": "СТ-011",
        "model": models_dict["Okuma GENOS M560-V"],
        "workshop": workshops_dict["Токарный цех"],
        "status": statuses_dict["Ожидание"],
        "load_percent": Decimal("8.75"),
        "commissioning_date": datetime(2024, 1, 30).date(),
    },
    {
        "inventory_number": "СТ-015",
        "model": models_dict["Doosan DNM 5700"],
        "workshop": workshops_dict["Токарный цех"],
        "status": statuses_dict["В производстве"],
        "load_percent": Decimal("88.20"),
        "commissioning_date": datetime(2022, 4, 18).date(),
    },
    {
        "inventory_number": "СТ-020",
        "model": models_dict["Fanuc Robodrill"],
        "workshop": workshops_dict["Токарный цех"],
        "status": statuses_dict["Неисправен"],
        "load_percent": Decimal("0.00"),
        "commissioning_date": datetime(2023, 3, 25).date(),
    },
    {
        "inventory_number": "СТ-022",
        "model": models_dict["Haas VF-2"],
        "workshop": workshops_dict["Сборочный цех"],
        "status": statuses_dict["Завершено"],
        "load_percent": Decimal("0.00"),
        "commissioning_date": datetime(2024, 6, 1).date(),
    },
    {
        "inventory_number": "СТ-025",
        "model": models_dict["DMG MORI CMX 1100 V"],
        "workshop": workshops_dict["Сборочный цех"],
        "status": statuses_dict["Ожидание"],
        "load_percent": Decimal("3.10"),
        "commissioning_date": datetime(2025, 2, 14).date(),
    },
    {
        "inventory_number": "СТ-030",
        "model": models_dict["Mazak VTC-200C"],
        "workshop": workshops_dict["Сборочный цех"],
        "status": statuses_dict["В производстве"],
        "load_percent": Decimal("45.60"),
        "commissioning_date": datetime(2023, 10, 30).date(),
    },
]

for data in machines_data:
    try:
        obj, created = Machine.objects.get_or_create(
            inventory_number=data["inventory_number"],
            defaults={
                "model": data["model"],
                "workshop": data["workshop"],
                "status": data["status"],
                "load_percent": data["load_percent"],
                "commissioning_date": data.get("commissioning_date"),
            }
        )
        if created:
            print(f"Создан станок: {obj.inventory_number} — {obj.model}")
        else:
            print(f"Станок уже существует: {obj.inventory_number}")
    except Exception as e:
        print(f"Ошибка при создании {data['inventory_number']}: {e}")

print("\nВсего станков в базе сейчас:", Machine.objects.count())


from datetime import datetime
from apps.core.models import Detail, Status  

# Получаем статус "Ожидание" (или другой начальный по умолчанию)
try:
    default_status = Status.objects.get(name="Ожидание")
except Status.DoesNotExist:
    default_status = Status.objects.first()  # если нет — берём первый
    print("Статус 'Ожидание' не найден, взят первый статус из базы.")

details_data = [
    {
        "article": "DET-101",
        "name": "Вал приводной",
        "drawing_number": "Ч-025-101",
        "planned_completion_date": datetime(2026, 4, 15, 18, 0),
        "status": default_status,
        "description": "Цилиндрический вал с шпонкой и резьбой M20×1.5",
    },
    {
        "article": "DET-205",
        "name": "Корпус подшипниковый",
        "drawing_number": "КД-18-205",
        "planned_completion_date": datetime(2026, 4, 20, 12, 0),
        "status": default_status,
        "description": "Корпус для радиально-упорного подшипника 7205",
    },
    {
        "article": "DET-312",
        "name": "Шестерня цилиндрическая Z=28",
        "drawing_number": "Ш-312",
        "planned_completion_date": datetime(2026, 5, 5, 16, 0),
        "status": default_status,
        "description": "Прямозубая шестерня модуль 2, ширина 25 мм",
    },
    {
        "article": "DET-408",
        "name": "Фланец крепежный",
        "drawing_number": "ФЛ-04-408",
        "planned_completion_date": datetime(2026, 4, 25, 18, 0),
        "status": default_status,
        "description": "Фланец Ø120 мм с 6 отверстиями под болты М10",
    },
    {
        "article": "DET-519",
        "name": "Втулка направляющая",
        "drawing_number": "ВТ-519",
        "planned_completion_date": datetime(2026, 5, 10, 12, 0),
        "status": default_status,
        "description": "Точная втулка Ø40×80 с внутренним Ø25 H7",
    },
    {
        "article": "DET-622",
        "name": "Кронштейн монтажный",
        "drawing_number": "КР-622",
        "planned_completion_date": datetime(2026, 4, 30, 15, 0),
        "status": default_status,
        "description": "Угловой кронштейн 150×100×8 мм с ребрами",
    },
    {
        "article": "DET-735",
        "name": "Поршень гидроцилиндра",
        "drawing_number": "П-07-735",
        "planned_completion_date": datetime(2026, 5, 12, 18, 0),
        "status": default_status,
        "description": "Поршень Ø80 мм с канавками под манжеты",
    },
    {
        "article": "DET-841",
        "name": "Крышка редуктора",
        "drawing_number": "КРШ-841",
        "planned_completion_date": datetime(2026, 5, 8, 12, 0),
        "status": default_status,
        "description": "Крышка с посадочным местом под подшипник 6205",
    },
    {
        "article": "DET-950",
        "name": "Пластина базовая",
        "drawing_number": "ПЛ-950",
        "planned_completion_date": datetime(2026, 5, 18, 16, 0),
        "status": default_status,
        "description": "Прямоугольная плита 300×200×20 с Т-пазами",
    },
    {
        "article": "DET-107",
        "name": "Шпиндель вспомогательный",
        "drawing_number": "ШП-107",
        "planned_completion_date": datetime(2026, 4, 18, 18, 0),
        "status": default_status,
        "description": "Тонкий шпиндель Ø25 с конусом Морзе 2",
    },
    {
        "article": "DET-214",
        "name": "Муфта соединительная",
        "drawing_number": "МФ-214",
        "planned_completion_date": datetime(2026, 5, 2, 12, 0),
        "status": default_status,
        "description": "Зубчатая муфта полужесткая Ø60 мм",
    },
    {
        "article": "DET-328",
        "name": "Рычаг переключения",
        "drawing_number": "РЧ-328",
        "planned_completion_date": datetime(2026, 5, 15, 15, 0),
        "status": default_status,
        "description": "Рычаг 180 мм с двумя отверстиями Ø12 и фасками",
    },
]

for data in details_data:
    try:
        obj, created = Detail.objects.get_or_create(
            article=data["article"],
            defaults={
                "name": data["name"],
                "drawing_number": data["drawing_number"],
                "planned_completion_date": data["planned_completion_date"],
                "status": data["status"],
                "description": data.get("description", ""),
            }
        )
        if created:
            print(f"Создана деталь: {obj.article} — {obj.name}")
        else:
            print(f"Деталь уже существует: {obj.article}")
    except Exception as e:
        print(f"Ошибка при создании {data['article']}: {e}")

print("\nВсего деталей в базе сейчас:", Detail.objects.count())


from apps.core.models import Stage, Detail, StageType, Machine  

# Вспомогательные словари для быстрого доступа
details    = {d.article: d for d in Detail.objects.all()}
stage_types = {st.name: st for st in StageType.objects.all()}
machines   = {m.inventory_number: m for m in Machine.objects.all()}

# Данные этапов (можно копировать-вставить целиком)
stages_data = [
    # DET-101
    {"detail": details["DET-101"], "stage_type": stage_types["Резка заготовки"],   "order_num": 1, "machine": machines["СТ-001"]},
    {"detail": details["DET-101"], "stage_type": stage_types["Токарная обработка"], "order_num": 2, "machine": machines["СТ-010"]},
    {"detail": details["DET-101"], "stage_type": stage_types["Фрезеровка"],        "order_num": 3, "machine": machines["СТ-005"]},
    {"detail": details["DET-101"], "stage_type": stage_types["Шлифовка"],          "order_num": 4, "machine": machines["СТ-002"]},

    # DET-205
    {"detail": details["DET-205"], "stage_type": stage_types["Резка заготовки"],   "order_num": 1, "machine": machines["СТ-008"]},
    {"detail": details["DET-205"], "stage_type": stage_types["Фрезеровка"],        "order_num": 2, "machine": machines["СТ-001"]},
    {"detail": details["DET-205"], "stage_type": stage_types["Сверление"],         "order_num": 3, "machine": machines["СТ-020"]},
    {"detail": details["DET-205"], "stage_type": stage_types["Шлифовка"],          "order_num": 4, "machine": machines["СТ-011"]},
    {"detail": details["DET-205"], "stage_type": stage_types["Контроль качества"], "order_num": 5, "machine": machines["СТ-015"]},

    # DET-312
    {"detail": details["DET-312"], "stage_type": stage_types["Резка заготовки"],   "order_num": 1, "machine": machines["СТ-002"]},
    {"detail": details["DET-312"], "stage_type": stage_types["Токарная обработка"], "order_num": 2, "machine": machines["СТ-010"]},
    {"detail": details["DET-312"], "stage_type": stage_types["Фрезеровка"],        "order_num": 3, "machine": machines["СТ-025"]},
    {"detail": details["DET-312"], "stage_type": stage_types["Термообработка"],    "order_num": 4, "machine": machines["СТ-005"]},  # условно

    # DET-408
    {"detail": details["DET-408"], "stage_type": stage_types["Резка заготовки"],   "order_num": 1, "machine": machines["СТ-030"]},
    {"detail": details["DET-408"], "stage_type": stage_types["Токарная обработка"], "order_num": 2, "machine": machines["СТ-011"]},
    {"detail": details["DET-408"], "stage_type": stage_types["Сверление"],         "order_num": 3, "machine": machines["СТ-020"]},
    {"detail": details["DET-408"], "stage_type": stage_types["Контроль качества"], "order_num": 4, "machine": machines["СТ-022"]},

    # DET-519 — только 3
    {"detail": details["DET-519"], "stage_type": stage_types["Токарная обработка"], "order_num": 1, "machine": machines["СТ-010"]},
    {"detail": details["DET-519"], "stage_type": stage_types["Шлифовка"],          "order_num": 2, "machine": machines["СТ-001"]},
    {"detail": details["DET-519"], "stage_type": stage_types["Контроль качества"], "order_num": 3, "machine": machines["СТ-015"]},

    # DET-622
    {"detail": details["DET-622"], "stage_type": stage_types["Резка заготовки"],   "order_num": 1, "machine": machines["СТ-005"]},
    {"detail": details["DET-622"], "stage_type": stage_types["Фрезеровка"],        "order_num": 2, "machine": machines["СТ-002"]},
    {"detail": details["DET-622"], "stage_type": stage_types["Сверление"],         "order_num": 3, "machine": machines["СТ-020"]},
    {"detail": details["DET-622"], "stage_type": stage_types["Контроль качества"], "order_num": 4, "machine": machines["СТ-030"]},

    # DET-735
    {"detail": details["DET-735"], "stage_type": stage_types["Резка заготовки"],   "order_num": 1, "machine": machines["СТ-001"]},
    {"detail": details["DET-735"], "stage_type": stage_types["Токарная обработка"], "order_num": 2, "machine": machines["СТ-010"]},
    {"detail": details["DET-735"], "stage_type": stage_types["Шлифовка"],          "order_num": 3, "machine": machines["СТ-002"]},
    {"detail": details["DET-735"], "stage_type": stage_types["Контроль качества"], "order_num": 4, "machine": machines["СТ-015"]},

    # DET-841
    {"detail": details["DET-841"], "stage_type": stage_types["Резка заготовки"],   "order_num": 1, "machine": machines["СТ-008"]},
    {"detail": details["DET-841"], "stage_type": stage_types["Фрезеровка"],        "order_num": 2, "machine": machines["СТ-025"]},
    {"detail": details["DET-841"], "stage_type": stage_types["Сверление"],         "order_num": 3, "machine": machines["СТ-020"]},
    {"detail": details["DET-841"], "stage_type": stage_types["Токарная обработка"], "order_num": 4, "machine": machines["СТ-011"]},
    {"detail": details["DET-841"], "stage_type": stage_types["Контроль качества"], "order_num": 5, "machine": machines["СТ-022"]},

    # DET-950
    {"detail": details["DET-950"], "stage_type": stage_types["Резка заготовки"],   "order_num": 1, "machine": machines["СТ-001"]},
    {"detail": details["DET-950"], "stage_type": stage_types["Фрезеровка"],        "order_num": 2, "machine": machines["СТ-005"]},
    {"detail": details["DET-950"], "stage_type": stage_types["Сверление"],         "order_num": 3, "machine": machines["СТ-020"]},
    {"detail": details["DET-950"], "stage_type": stage_types["Контроль качества"], "order_num": 4, "machine": machines["СТ-030"]},

    # DET-107
    {"detail": details["DET-107"], "stage_type": stage_types["Резка заготовки"],   "order_num": 1, "machine": machines["СТ-010"]},
    {"detail": details["DET-107"], "stage_type": stage_types["Токарная обработка"], "order_num": 2, "machine": machines["СТ-011"]},
    {"detail": details["DET-107"], "stage_type": stage_types["Фрезеровка"],        "order_num": 3, "machine": machines["СТ-002"]},
    {"detail": details["DET-107"], "stage_type": stage_types["Шлифовка"],          "order_num": 4, "machine": machines["СТ-001"]},

    # DET-214
    {"detail": details["DET-214"], "stage_type": stage_types["Резка заготовки"],   "order_num": 1, "machine": machines["СТ-001"]},
    {"detail": details["DET-214"], "stage_type": stage_types["Токарная обработка"], "order_num": 2, "machine": machines["СТ-010"]},
    {"detail": details["DET-214"], "stage_type": stage_types["Фрезеровка"],        "order_num": 3, "machine": machines["СТ-025"]},
    {"detail": details["DET-214"], "stage_type": stage_types["Контроль качества"], "order_num": 4, "machine": machines["СТ-015"]},

    # DET-328 — только 3
    {"detail": details["DET-328"], "stage_type": stage_types["Резка заготовки"],   "order_num": 1, "machine": machines["СТ-030"]},
    {"detail": details["DET-328"], "stage_type": stage_types["Фрезеровка"],        "order_num": 2, "machine": machines["СТ-002"]},
    {"detail": details["DET-328"], "stage_type": stage_types["Сверление"],         "order_num": 3, "machine": machines["СТ-020"]},
]

created_count = 0
for data in stages_data:
    try:
        obj, created = Stage.objects.get_or_create(
            detail=data["detail"],
            order_num=data["order_num"],
            defaults={
                "stage_type": data["stage_type"],
                "machine": data["machine"],
                "is_completed": False,
                "notes": ""
            }
        )
        if created:
            created_count += 1
            print(f"Создан этап {data['order_num']} для {data['detail'].article}")
        # detail.recalculate_completion() вызовется автоматически благодаря save() в модели
    except Exception as e:
        print(f"Ошибка для {data['detail'].article} этап {data['order_num']}: {e}")

print(f"\nСоздано новых этапов: {created_count}")
print("Общее количество этапов в базе:", Stage.objects.count())


from datetime import datetime
from apps.core.models import MachineAssignment, Machine, Detail  

# Вспомогательные словари
machines = {m.inventory_number: m for m in Machine.objects.filter(inventory_number__in=[
    "СТ-001", "СТ-002", "СТ-005", "СТ-010", "СТ-020"
])}

details = {d.article: d for d in Detail.objects.all()}

assignments_data = [
    # СТ-001
    {
        "machine": machines["СТ-001"],
        "detail": details["DET-101"],
        "planned_start": datetime(2026, 3, 5, 8, 0),
        "planned_end": datetime(2026, 3, 7, 16, 0),
        "notes": "Резка + шлифовка вала DET-101"
    },
    {
        "machine": machines["СТ-001"],
        "detail": details["DET-735"],
        "planned_start": datetime(2026, 3, 10, 8, 0),
        "planned_end": datetime(2026, 3, 11, 16, 0),
        "notes": "Резка поршня"
    },
    {
        "machine": machines["СТ-001"],
        "detail": details["DET-950"],
        "planned_start": datetime(2026, 3, 12, 13, 0),
        "planned_end": datetime(2026, 3, 13, 18, 0),
        "notes": "Резка пластины базовой"
    },

    # СТ-010 (токарка — много задач)
    {
        "machine": machines["СТ-010"],
        "detail": details["DET-101"],
        "planned_start": datetime(2026, 3, 6, 8, 0),
        "planned_end": datetime(2026, 3, 8, 16, 0),
        "notes": "Токарная обработка вала"
    },
    {
        "machine": machines["СТ-010"],
        "detail": details["DET-519"],
        "planned_start": datetime(2026, 3, 7, 8, 0),
        "planned_end": datetime(2026, 3, 8, 12, 0),
        "notes": "Токарка втулки направляющей"
    },
    {
        "machine": machines["СТ-010"],
        "detail": details["DET-312"],
        "planned_start": datetime(2026, 3, 11, 8, 0),
        "planned_end": datetime(2026, 3, 12, 16, 0),
        "notes": "Токарная черновая шестерни"
    },

    # СТ-002
    {
        "machine": machines["СТ-002"],
        "detail": details["DET-101"],
        "planned_start": datetime(2026, 3, 8, 8, 0),
        "planned_end": datetime(2026, 3, 9, 16, 0),
        "notes": "Финишная шлифовка вала"
    },
    {
        "machine": machines["СТ-002"],
        "detail": details["DET-107"],
        "planned_start": datetime(2026, 3, 14, 8, 0),
        "planned_end": datetime(2026, 3, 15, 16, 0),
        "notes": "Фрезеровка + шлифовка шпинделя"
    },

    # СТ-005 (низкая загрузка → можно загружать)
    {
        "machine": machines["СТ-005"],
        "detail": details["DET-622"],
        "planned_start": datetime(2026, 3, 5, 8, 0),
        "planned_end": datetime(2026, 3, 6, 16, 0),
        "notes": "Резка кронштейна"
    },

    # СТ-020 (неисправен → назначение для теста)
    {
        "machine": machines["СТ-020"],
        "detail": details["DET-205"],
        "planned_start": datetime(2026, 3, 10, 8, 0),
        "planned_end": datetime(2026, 3, 10, 14, 0),
        "notes": "Сверление корпуса — тест на неисправный станок"
    },
]

created_count = 0
for data in assignments_data:
    try:
        obj, created = MachineAssignment.objects.get_or_create(
            machine=data["machine"],
            detail=data["detail"],
            planned_start=data["planned_start"],
            defaults={
                "planned_end": data["planned_end"],
                "notes": data.get("notes", ""),
                "actual_start": None,
                "actual_end": None,
            }
        )
        if created:
            created_count += 1
            print(f"Создано назначение: {data['machine'].inventory_number} → {data['detail'].article}")
        else:
            print(f"Уже существует: {data['machine'].inventory_number} → {data['detail'].article}")
    except Exception as e:
        print(f"Ошибка: {data['machine'].inventory_number} → {data['detail'].article}: {e}")

print(f"\nСоздано новых назначений: {created_count}")
print("Всего назначений в базе:", MachineAssignment.objects.count())


from datetime import datetime
from apps.core.models import MachineAssignment, Machine, Detail  # замени 'app' на своё приложение

machines = {m.inventory_number: m for m in Machine.objects.filter(inventory_number__in=[
    "СТ-001", "СТ-002", "СТ-005", "СТ-010"
])}

details = {d.article: d for d in Detail.objects.all()}

past_and_current_assignments = [

    # Прошлые завершённые
    {"machine": machines["СТ-001"], "detail": details["DET-622"],
     "planned_start": datetime(2026, 1, 20, 8), "planned_end": datetime(2026, 1, 22, 16),
     "actual_start": datetime(2026, 1, 20, 8, 30), "actual_end": datetime(2026, 1, 22, 15, 45),
     "notes": "Фрезеровка кронштейна — завершено"},

    {"machine": machines["СТ-001"], "detail": details["DET-107"],
     "planned_start": datetime(2026, 2, 10, 8), "planned_end": datetime(2026, 2, 12, 16),
     "actual_start": datetime(2026, 2, 10, 9), "actual_end": datetime(2026, 2, 12, 14, 30),
     "notes": "Шлифовка шпинделя — завершено"},

    {"machine": machines["СТ-002"], "detail": details["DET-735"],
     "planned_start": datetime(2026, 2, 5, 8), "planned_end": datetime(2026, 2, 6, 16),
     "actual_start": datetime(2026, 2, 5, 8, 15), "actual_end": datetime(2026, 2, 6, 17, 10),
     "notes": "Шлифовка поршня — небольшая просрочка"},

    {"machine": machines["СТ-010"], "detail": details["DET-408"],
     "planned_start": datetime(2026, 1, 15, 8), "planned_end": datetime(2026, 1, 16, 16),
     "actual_start": datetime(2026, 1, 15, 8), "actual_end": datetime(2026, 1, 16, 15, 20),
     "notes": "Токарная фланца — завершено"},

    {"machine": machines["СТ-010"], "detail": details["DET-214"],
     "planned_start": datetime(2026, 2, 20, 8), "planned_end": datetime(2026, 2, 21, 16),
     "actual_start": datetime(2026, 2, 20, 8, 45), "actual_end": datetime(2026, 2, 21, 16, 30),
     "notes": "Токарная муфты — завершено"},

    {"machine": machines["СТ-005"], "detail": details["DET-950"],
     "planned_start": datetime(2026, 2, 1, 8), "planned_end": datetime(2026, 2, 2, 16),
     "actual_start": datetime(2026, 2, 1, 8), "actual_end": datetime(2026, 2, 2, 15, 50),
     "notes": "Фрезеровка пазов пластины — завершено"},

    # Текущие (идут сейчас)
    {"machine": machines["СТ-001"], "detail": details["DET-101"],
     "planned_start": datetime(2026, 3, 1, 8), "planned_end": datetime(2026, 3, 4, 16),
     "actual_start": datetime(2026, 3, 1, 8, 20), "actual_end": None,
     "notes": "Шлифовка вала — в работе"},

    {"machine": machines["СТ-002"], "detail": details["DET-312"],
     "planned_start": datetime(2026, 3, 2, 8), "planned_end": datetime(2026, 3, 5, 16),
     "actual_start": datetime(2026, 3, 2, 9), "actual_end": None,
     "notes": "Фрезеровка шестерни — в работе"},

    {"machine": machines["СТ-010"], "detail": details["DET-101"],
     "planned_start": datetime(2026, 3, 3, 8), "planned_end": datetime(2026, 3, 6, 16),
     "actual_start": datetime(2026, 3, 3, 8, 10), "actual_end": None,
     "notes": "Токарная вала — идёт сейчас"},
]

created_count = 0
for data in past_and_current_assignments:
    try:
        obj, created = MachineAssignment.objects.get_or_create(
            machine=data["machine"],
            detail=data["detail"],
            planned_start=data["planned_start"],
            defaults={
                "planned_end": data["planned_end"],
                "actual_start": data.get("actual_start"),
                "actual_end": data.get("actual_end"),
                "notes": data.get("notes", ""),
            }
        )
        if created:
            created_count += 1
            status = "текущее" if data.get("actual_end") is None else "прошлое"
            print(f"Добавлено {status} назначение: {data['machine'].inventory_number} → {data['detail'].article}")
        else:
            print(f"Уже существует: {data['machine'].inventory_number} → {data['detail'].article}")
    except Exception as e:
        print(f"Ошибка: {e}")

print(f"\nДобавлено новых назначений: {created_count}")
print("Всего назначений теперь:", MachineAssignment.objects.count())