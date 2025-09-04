from django.db import models
from django.utils import timezone
import uuid

class ChatSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    user_name = models.CharField(max_length=100, blank=True)
    user_email = models.EmailField(blank=True)
    user_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Chat {self.session_id} - {self.user_name or 'Anonymous'}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('admin', 'Admin')
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

class AutoResponse(models.Model):
    keywords = models.TextField(help_text="Từ khóa (cách nhau bởi dấu phẩy)")
    response = models.TextField(help_text="Phản hồi tự động")
    priority = models.IntegerField(default=0, help_text="Ưu tiên (số cao hơn = ưu tiên cao hơn)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"Auto Response: {self.keywords[:30]}..."

    def get_keywords_list(self):
        return [k.strip().lower() for k in self.keywords.split(',')]
