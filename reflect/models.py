from django.db import models
from django.contrib.auth.models import User

class Reflect(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reflections")
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    response = models.TextField(blank=True, null=True)  # Giáo viên phản hồi

    def __str__(self):
        return self.title
    
# Lĩnh vực / Loại phản ánh
class Type(models.Model):
    name_type = models.CharField(max_length=100, unique=True)
    content = models.TextField(blank=True)  # 👈 thêm dòng này

    def __str__(self):
        return self.name_type

class Document(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='documents/')  # Lưu file vào thư mục /media/documents/

    def __str__(self):
        return self.name