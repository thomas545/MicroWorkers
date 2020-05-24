from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Category, Task

class CategoryAdmin(TranslationAdmin):
    pass


class TaskAdmin(admin.ModelAdmin):
    pass

admin.site.register(Category, CategoryAdmin)
admin.site.register(Task, TaskAdmin)