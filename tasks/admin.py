from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Category, Task, TaskDeal

@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    pass

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass

@admin.register(TaskDeal)
class TaskDealAdmin(admin.ModelAdmin):
    pass