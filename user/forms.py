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
    class Meta:
        model = SV
        fields = [
            "email", "ho_ten", "ngay_sinh", "gioi_tinh", "noi_sinh", "dan_toc", "que_quan",
            "so_hieu_cong_an", "can_cuoc", "ngay_cap", "noi_cap",
            "dia_chi_lien_lac", "dien_thoai", "lop", "khoa", "status"
        ]


# ================== GIẢNG VIÊN ================== #
class GVForm(BaseUserLinkedForm):
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
