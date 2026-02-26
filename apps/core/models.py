from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# ============================================================
# БАЗОВАЯ МОДЕЛЬ
# ============================================================

class BaseModel(models.Model):
    """
    Абстрактная базовая модель.

    Добавляет:
    - дату создания
    - дату изменения
    - мягкое удаление

    Используется всеми моделями системы.
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        help_text="Автоматически устанавливается при создании записи"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата изменения",
        help_text="Автоматически обновляется при каждом сохранении записи"
    )

    is_deleted = models.BooleanField(
        default=False,
        verbose_name="Удалено",
        help_text="Пометка для мягкого удаления записи (без фактического удаления из БД)"
    )

    class Meta:
        abstract = True


# ============================================================
# СПРАВОЧНИК СТАТУСОВ
# ============================================================

class Status(BaseModel):
    """
    Справочник статусов.

    Используется:
    - для деталей
    - для станков
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название",
        help_text='Например: "В работе", "Завершено", "Ожидание", "Неисправен"'
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Дополнительная информация о статусе"
    )

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ["name"]

    def __str__(self):
        return self.name
    

# ============================================================
# СПРАВОЧНИК ЭТАПОВ
# ============================================================

class StageType(BaseModel):
    """
    Справочник типов этапов обработки детали.
    """

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название этапа",
        help_text='Например: "Фрезеровка", "Токарная обработка", "Термообработка"'
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Подробное описание данного этапа"
    )

    class Meta:
        verbose_name = "Тип этапа"
        verbose_name_plural = "Типы этапов"
        ordering = ["name"]

    def __str__(self):
        return self.name
    

# ============================================================
# СПРАВОЧНИК МОДЕЛЕЙ СТАНКОВ
# ============================================================

class MachineModel(BaseModel):
    """
    Справочник моделей станков.
    """

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название модели",
        help_text='Например: "Haas VF-2", "DMG MORI CMX 1100 Vc"'
    )

    manufacturer = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Производитель"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Технические характеристики и особенности модели"
    )

    class Meta:
        verbose_name = "Модель станка"
        verbose_name_plural = "Модели станков"
        ordering = ["name"]

    def __str__(self):
        return self.name
    

# ============================================================
# СПРАВОЧНИК ЦЕХОВ
# ============================================================

class Workshop(BaseModel):
    """
    Справочник цехов предприятия.
    """

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название цеха",
        help_text='Например: "Механический цех №1", "Сборочный цех"'
    )

    code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        verbose_name="Код цеха",
        help_text='Краткое обозначение, например: "МЦ-01"'
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Расположение, начальник цеха, особенности"
    )

    class Meta:
        verbose_name = "Цех"
        verbose_name_plural = "Цеха"
        ordering = ["code", "name"]

    def __str__(self):
        return self.name
    
# ============================================================
# СТАНКИ
# ============================================================

class Machine(BaseModel):
    """
    Модель станка.

    Описывает оборудование предприятия.
    """

    inventory_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Инвентарный номер",
        help_text="Уникальный инвентарный номер станка на предприятии"
    )

    model = models.ForeignKey(
        MachineModel,
        on_delete=models.PROTECT,
        related_name="machines",
        verbose_name="Модель",
        help_text="Ссылка на модель станка из справочника"
    )

    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.PROTECT,
        related_name="machines",
        verbose_name="Цех",
        help_text="Цех, в котором установлен станок",
    )

    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="machines",
        verbose_name="Статус",
        help_text="Текущее состояние станка (работает, ремонт, ожидание и т.д.)"
    )

    load_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Загрузка (%)",
    )

    commissioning_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата ввода в эксплуатацию"
    )

    last_maintenance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата последнего ТО",
        help_text="Дата последнего технического обслуживания"
    )

    class Meta:
        verbose_name = "Станок"
        verbose_name_plural = "Станки"
        ordering = ["model", "inventory_number"]
        indexes = [
            models.Index(fields=["inventory_number"]),
            models.Index(fields=["model"]),
            models.Index(fields=["status"]),
            models.Index(fields=["workshop"]),
        ]

    def __str__(self):
        return f"{self.model} ({self.workshop})"


# ============================================================
# ДЕТАЛИ
# ============================================================

class Detail(BaseModel):
    """
    Основная модель деталей.

    Хранит информацию о производимых деталях.
    """

    article = models.CharField(
        max_length=100,
        verbose_name="Артикул",
        help_text="Артикул детали в системе учёта"
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Название",
        help_text="Полное наименование детали"
    )

    drawing_number = models.CharField(
        max_length=100,
        verbose_name="Номер чертежа",
        help_text="Номер чертежа или КД"
    )

    planned_completion_date = models.DateTimeField(
        verbose_name="Плановая дата готовности",
        null=True,
        blank=True
    )

    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="details",
        verbose_name="Статус"
    )

    completion_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Готовность (%)",
        help_text="Рассчитывается автоматически на основе выполненных этапов"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Дополнительная информация о детали"
    )

    class Meta:
        verbose_name = "Деталь"
        verbose_name_plural = "Детали"
        ordering = ["article"]
        indexes = [
            models.Index(fields=["article"]),
            models.Index(fields=["drawing_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["planned_completion_date"]),
        ]

    def __str__(self):
        return f"{self.article} - {self.name}"

    def recalculate_completion(self):
        """
        Пересчитывает процент готовности детали.

        Формула:

        completed_stages / total_stages * 100
        """

        total = self.stages.filter(is_deleted=False).count()

        if total == 0:
            self.completion_percent = 0
            self.save(update_fields=["completion_percent"])
            return

        completed = self.stages.filter(
            is_completed=True,
            is_deleted=False
        ).count()

        percent = (completed / total) * 100

        self.completion_percent = round(percent, 2)

        self.save(update_fields=["completion_percent"])


# ============================================================
# ЭТАПЫ ОБРАБОТКИ
# ============================================================

class Stage(BaseModel):
    """
    Этап обработки детали.

    Каждый этап:
    - принадлежит детали
    - привязан к станку
    - имеет порядок выполнения
    """

    detail = models.ForeignKey(
        Detail,
        on_delete=models.CASCADE,
        related_name="stages",
        verbose_name="Деталь",
        help_text="Деталь, для которой определён этот этап"
    )

    stage_type = models.ForeignKey(
        StageType,
        on_delete=models.PROTECT,
        related_name="stages",
        verbose_name="Название этапа",
        help_text="Ссылка на название этапа из справочника"
    )

    order_num = models.PositiveIntegerField(
        verbose_name="Порядковый номер",
        help_text="Порядок выполнения этапа в технологическом маршруте"
    )

    machine = models.ForeignKey(
        Machine,
        on_delete=models.PROTECT,
        related_name="stages",
        verbose_name="Станок",
        help_text="Станок, на котором выполняется этот этап"
    )

    is_completed = models.BooleanField(
        default=False,
        verbose_name="Выполнен"
    )

    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата выполнения",
        help_text="Отметка о выполнении этапа"
    )

    # planned_duration_hours = models.PositiveIntegerField(
    #     blank=True,
    #     null=True,
    #     verbose_name="Плановая длительность (часы)",
    #     help_text="Планируемое время на выполнение этапа"
    # )

    notes = models.TextField(
        blank=True,
        verbose_name="Примечания",
        help_text="Особые отметки по выполнению этапа"
    )

    class Meta:
        verbose_name = "Этап обработки"
        verbose_name_plural = "Этапы обработки"
        ordering = ["detail", "order_num"]

        unique_together = (
            "detail",
            "order_num",
        )

        indexes = [
            models.Index(fields=["detail"]),
            models.Index(fields=["machine"]),
        ]

    def __str__(self):
        return f"{self.detail} - Этап {self.order_num}"

    def save(self, *args, **kwargs):
        """
        При сохранении этапа автоматически
        пересчитывается процент готовности детали.
        """

        super().save(*args, **kwargs)

        self.detail.recalculate_completion()


# ============================================================
# НАЗНАЧЕНИЕ НА СТАНКИ
# ============================================================

class MachineAssignment(BaseModel):
    """
    Назначение деталей на станки.

    Используется для планирования загрузки.
    """

    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Станок",
        help_text="Станок, на который назначается деталь"
    )

    detail = models.ForeignKey(
        Detail,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Деталь",
        help_text="Деталь, которая будет обрабатываться"
    )

    assignment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата назначения"
    )

    planned_start = models.DateTimeField(
        verbose_name="Плановое начало",
        help_text="Планируемая дата и время начала обработки"
    )

    actual_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Фактическое начало",
        help_text="Фактическая дата и время начала обработки"
    )

    planned_end = models.DateTimeField(
        verbose_name="Плановое завершение",
        help_text="Планируемая дата и время завершения обработки"
    )

    actual_end = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Фактическое завершение",
        help_text="Фактическая дата и время завершения обработки"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Примечания",
        help_text="Дополнительная информация о назначении"
    )

    class Meta:
        verbose_name = "Назначение на станок"
        verbose_name_plural = "Назначения на станки"
        ordering = ["-planned_start"]

        indexes = [
            models.Index(fields=["machine"]),
            models.Index(fields=["detail"]),
            models.Index(fields=["actual_start", "actual_end"]),
        ]

    def __str__(self):
        return f"{self.machine} → {self.detail}"


class LogEntry(BaseModel):
    """
    Журнал действий пользователей.

    Используется для:
    - аудита
    - расследований
    - истории изменений
    """

    ACTION_CHOICES = [

        ("CREATE", "Создание"),
        ("UPDATE", "Изменение"),
        ("DELETE", "Удаление"),
        ("STATUS_CHANGE", "Смена статуса"),
        ("STAGE_COMPLETE", "Этап выполнен"),
        ("RECALCULATE", "Пересчет готовности"),
        ("ASSIGNMENT", "Назначение на станок"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь",
        related_name="system_logs",
    )

    action_type = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        verbose_name="Тип действия"
    )

    entity_type = models.CharField(
        max_length=50,
        verbose_name="Тип объекта"
    )

    entity_id = models.PositiveIntegerField(
        verbose_name="ID объекта"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    changes_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Изменения"
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Запись журнала"
        verbose_name_plural = "Журнал действий"

        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["action_type"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]

    def __str__(self):

        return f"{self.created_at} {self.action_type}"