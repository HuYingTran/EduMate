from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserSVRegistrationForm(UserCreationForm):
    ho_ten = forms.CharField(max_length=255)
    ngay_sinh = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    gioi_tinh = forms.ChoiceField(choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')])
    noi_sinh = forms.CharField(max_length=255)
    dan_toc = forms.CharField(max_length=50)
    que_quan = forms.CharField(max_length=255)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "ho_ten", "ngay_sinh", "gioi_tinh", "noi_sinh", "dan_toc", "que_quan", "email")


from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class StudentLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        # Nếu user có SV -> check status
        if hasattr(user, "sv") and user.sv.status != "A":
            raise ValidationError(
                "Tài khoản Sinh viên chưa được kích hoạt. Vui lòng chờ Admin duyệt.",
                code="inactive",
            )
        # Nếu không phải SV thì dùng mặc định (admin, GV,...)
        return super().confirm_login_allowed(user)


from django import forms
from django.contrib.auth.models import User
from .models import GV

class GVRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = GV
        fields = ["ho_ten", "ngay_sinh", "gioi_tinh", "email", "so_dien_thoai", "bo_mon", "chuc_vu"]

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"]
        )
        gv = super().save(commit=False)
        gv.user = user
        if commit:
            gv.save()
        return gv
