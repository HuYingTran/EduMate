from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("question", "answer", "user", "created_at")
    search_fields = ("question", "answer")
    list_filter = ("created_at",)
