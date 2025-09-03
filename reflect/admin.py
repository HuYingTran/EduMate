from django.contrib import admin
from .models import Type, Document, ReflectResponse, Reflect
# Register your models here.
@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ("name_type",)
    search_fields = ("name_type",)
    
@admin.register(Reflect)
class ReflectAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    
@admin.register(ReflectResponse)
class ReflectResponseAdmin(admin.ModelAdmin):
    list_display = ("reflect",)
    search_fields = ("reflect",)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)