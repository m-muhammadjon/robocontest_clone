from django.contrib import admin

from .models import *


class SampleItemInline(admin.TabularInline):
    model = Sample
    raw_id_fields = ['problem']


class TestItemInline(admin.TabularInline):
    model = TestCase
    raw_id_fields = ['problem']
    extra = 10


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'hidden']
    inlines = [SampleItemInline, TestItemInline]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'problem', 'lang', 'time', 'verdict', 'contest']
    list_filter = ['user', 'problem', 'lang']


class ContestProblemInline(admin.TabularInline):
    model = ContestProblem
    raw_id_fields = ['contest']


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    inlines = [ContestProblemInline]


admin.site.register(ProgrammingLanguage)
admin.site.register(ContestResult)
admin.site.register(ContestProblem)
