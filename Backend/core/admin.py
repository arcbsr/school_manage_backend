from django.contrib import admin
from .models import Branch, Shift, AcademicSession, SchoolClass, Section, Subject


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "address")


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "start_time", "end_time", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "branch", "shift", "academic_session", "is_active")
    list_filter = ("is_active", "branch", "shift", "academic_session")
    search_fields = ("name",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "school_class", "is_active")
    list_filter = ("is_active", "school_class")
    search_fields = ("name",)


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "year", "is_active", "is_current")
    list_filter = ("is_active", "is_current")
    search_fields = ("year",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")

# Register your models here.
