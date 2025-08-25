from django.db import models
from django.contrib.auth.models import User

class SV(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='sv'
    )

    # Thông tin cơ bản
    ho_ten = models.CharField(max_length=255, verbose_name="Họ và tên")
    ngay_sinh = models.DateField(verbose_name="Ngày sinh")
    gioi_tinh = models.CharField(
        max_length=10,
        choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')],
        verbose_name="Giới tính"
    )
    noi_sinh = models.CharField(max_length=255, verbose_name="Nơi sinh")
    dan_toc = models.CharField(max_length=50, verbose_name="Dân tộc")
    que_quan = models.CharField(max_length=255, verbose_name="Quê quán")
    email = models.EmailField(verbose_name="Địa chỉ email")

    # Thông tin giấy tờ
    so_hieu_cong_an = models.CharField(max_length=50, verbose_name="Số hiệu Công an nhân dân", blank=True, null=True)
    can_cuoc = models.CharField(max_length=20, verbose_name="Căn cước công dân", blank=True, null=True)
    ngay_cap = models.DateField(verbose_name="Ngày cấp", blank=True, null=True)
    noi_cap = models.CharField(max_length=255, verbose_name="Nơi cấp", blank=True, null=True)

    # Liên lạc
    dia_chi_lien_lac = models.CharField(max_length=255, verbose_name="Địa chỉ liên lạc", blank=True, null=True)
    dien_thoai = models.CharField(max_length=15, verbose_name="Điện thoại di động", blank=True, null=True)
    
    # Thông tin lớp
    lop = models.CharField(max_length=255, verbose_name="Lớp", blank=True, null=True)
    khoa = models.CharField(max_length=255, verbose_name="Khóa", blank=True, null=True)
    
    STATUS_CHOICES = [
        ('P', "Pending"),
        ('A', "Active"),
        ('R', "Rejected"),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return self.ho_ten

class GV(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ho_ten = models.CharField(max_length=255)

    def __str__(self):
        return self.ho_ten

from django.db import models
from django.contrib.auth.models import User

class GV(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='gv'
    )

    # Thông tin cơ bản
    ho_ten = models.CharField(max_length=255, verbose_name="Họ và tên")
    ngay_sinh = models.DateField(verbose_name="Ngày sinh")
    gioi_tinh = models.CharField(
        max_length=10,
        choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')],
        verbose_name="Giới tính"
    )
    email = models.EmailField(verbose_name="Email", unique=True)
    so_dien_thoai = models.CharField(max_length=15, verbose_name="Điện thoại", blank=True, null=True)

    # Chức vụ / khoa
    bo_mon = models.CharField(max_length=255, verbose_name="Bộ môn", blank=True, null=True)
    chuc_vu = models.CharField(max_length=255, verbose_name="Chức vụ", blank=True, null=True)

    STATUS_CHOICES = [
        ('P', "Pending"),
        ('A', "Active"),
        ('R', "Rejected"),
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return self.ho_ten
