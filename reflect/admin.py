from django.contrib import admin
from .models import Type
# Register your models here.
@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ("name_type",)
    search_fields = ("name_type",)