from django.db import models
from django.contrib.auth.models import User
from user.models import BoMon

# Lĩnh vực / Loại phản ánh
class Type(models.Model):
    name_type = models.CharField(max_length=100, unique=True)
    content = models.TextField(blank=True)  # 👈 thêm dòng này

    def __str__(self):
        return self.name_type

# Phản ánh của sinh viên
class Reflect(models.Model):
    STATUS_CHOICES = [
        ("create", "Đã tạo"),
        ("active", "Đã xử lý"),
        ("done", "Hoàn thành"),
        ("cancel", "Đã hủy"),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reflections")
    title = models.CharField(max_length=200)
    content = models.TextField()
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True, blank=True, related_name="reflects")
    bo_mon = models.ForeignKey(BoMon, on_delete=models.SET_NULL, null=True, blank=True, related_name="reflects")
    attachment = models.FileField(upload_to="reflect_attachments/", null=True, blank=True)
    anonymous = models.BooleanField(default=False)   # 🔹 thêm trường ẩn danh
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="create"
    )

    def __str__(self):
        return f"{self.title} - {self.student}"

    @property
    def display_student(self):
        """Trả về tên SV hoặc 'Ẩn danh' nếu chọn ẩn danh"""
        if self.anonymous:
            return "Ẩn danh"
        if hasattr(self.student, "sv"):
            return self.student.sv.ho_ten
        return self.student.username

# Phản hồi của giáo viên
class ReflectResponse(models.Model):
    reflect = models.ForeignKey(Reflect, on_delete=models.CASCADE, related_name="responses")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reflect_responses")
    content = models.TextField()
    attachment = models.FileField(upload_to="reflect_response_attachments/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveSmallIntegerField(default=0)  # đánh giá từ sinh viên

    def __str__(self):
        return f"Response by {self.teacher} on {self.reflect.title}"
    

class Document(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='documents/')  # Lưu file vào thư mục /media/documents/

    def __str__(self):
        return self.name
    
from django.db import models

# class Survey(models.Model):
#     STATUS_CHOICES = [
#         ('active', 'Đang mở'),
#         ('inactive', 'Tạm dừng'),
#         ('closed', 'Đã đóng'),
#     ]

#     title = models.CharField("Tiêu đề khảo sát", max_length=255)
#     link = models.URLField("Link khảo sát")
#     status = models.CharField("Trạng thái", max_length=10, choices=STATUS_CHOICES, default='active')
#     end_date = models.DateField("Ngày kết thúc", null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)  # tự động lưu ngày tạo
#     updated_at = models.DateTimeField(auto_now=True)      # tự động lưu ngày cập nhật

#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = "Khảo sát"
#         verbose_name_plural = "Khảo sát"

#     def __str__(self):
#         return self.title

from django.contrib.auth.models import User

@property
def is_teacher(self):
    return hasattr(self, "gv") and self.gv.status == "A"

User.add_to_class("is_teacher", is_teacher)

# models.py
from django.db import models
from django.contrib.auth.models import User

class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = [
        ('choice', 'Multiple Choice'),
        ('text', 'Text'),
        ('rating', 'Rating (1-5)'),
    ]
    
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']

class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True)
    choice_answer = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    rating_answer = models.PositiveIntegerField(null=True, blank=True)