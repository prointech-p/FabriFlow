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