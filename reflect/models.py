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
