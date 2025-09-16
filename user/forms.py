from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import SV, GV

# ----- Base form dùng chung -----
class BaseUserLinkedForm(forms.ModelForm):
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        abstract = True  # Form cha, không dùng trực tiếp

    def save(self, commit=True):
        # Tạo User mới nếu chưa tồn tại
        email = self.cleaned_data["email"]
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                "email": email,
                "password": make_password("123456")  # mật khẩu mặc định
            }
        )
        self.instance.user = user
        return super().save(commit=commit)


# ================== SINH VIÊN ================== #
class SVForm(BaseUserLinkedForm):
    ngay_sinh = forms.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],  # Cho phép nhập DD/MM/YYYY hoặc YYYY-MM-DD
        widget=forms.DateInput(attrs={
            'type': 'date',  # HTML5 date picker
            'class': 'form-control',
        })
    )
    class Meta:
        model = SV
        fields = "__all__"
        fields = [
            "email", "ho_ten", "ngay_sinh", "gioi_tinh", "noi_sinh", "dan_toc", "que_quan",
            "so_hieu_cong_an", "can_cuoc", "ngay_cap", "noi_cap",
            "dia_chi_lien_lac", "dien_thoai", "lop", "khoa", "status"
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Giá trị mặc định khi thêm mới
        if not self.instance.pk:  # Chỉ khi tạo mới
            self.fields['dan_toc'].initial = "Kinh"
            self.fields['noi_cap'].initial = " Cục Cảnh sát quản lý hành chính về trật tự xã hội"
            self.fields['dia_chi_lien_lac'].initial = "Trường Đại học Kỹ thuật - Hậu cần CAND"

# ================== GIẢNG VIÊN ================== #
class GVForm(BaseUserLinkedForm):
    ngay_sinh = forms.DateField(
        input_formats=['%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })
    )
    class Meta:
        model = GV
        fields = [
            "email", "ho_ten", "ngay_sinh", "gioi_tinh", "so_dien_thoai",
            "can_cuoc", "ngay_cap", "noi_cap",
            "bo_mon", "chuc_vu", "status"
        ]


from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class CustomLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        # Nếu là SV
        if hasattr(user, "sv") and user.sv.status != "A":
            raise ValidationError(
                "Tài khoản Sinh viên chưa được kích hoạt. Vui lòng chờ Admin duyệt.",
                code="inactive",
            )
        # Nếu là GV
        if hasattr(user, "gv") and user.gv.status != "A":
            raise ValidationError(
                "Tài khoản Giảng viên chưa được kích hoạt. Vui lòng chờ Admin duyệt.",
                code="inactive",
            )

from django import forms
from .models import BoMon

class BoMonForm(forms.ModelForm):
    class Meta:
        model = BoMon
        fields = ["ten"]
