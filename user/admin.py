from django.contrib import admin
from .models import SV, GV, BoMon

@admin.register(SV)
class SVAdmin(admin.ModelAdmin):
    list_display = ("ho_ten", "ngay_sinh", "gioi_tinh", "email")
    search_fields = ("ho_ten", "email")

@admin.register(GV)
class GVAdmin(admin.ModelAdmin):
    list_display = ("ho_ten",)
    search_fields = ("ho_ten",)

@admin.register(BoMon)
class BoMonAdmin(admin.ModelAdmin):
    list_display = ("ten",)
    search_fields = ("ten",)