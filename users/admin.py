from django.contrib import admin
from django.contrib.auth.models import Group
from . import models

admin.site.unregister(Group)

admin.site.register(models.Profile)
admin.site.register(models.Address)
admin.site.register(models.Skill)
