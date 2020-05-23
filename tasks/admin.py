from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Category

class CategoryAdmin(TranslationAdmin):
    pass

admin.site.register(Category, CategoryAdmin)