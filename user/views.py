from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import SV, GV, BoMon
from .forms import SVForm, GVForm


# ----- CSRF failure handler -----
def csrf_failure(request, reason=""):
    return render(request, "csrf_failure.html", {"reason": reason})


# ----- Mixin chung để thêm context -----
class ObjectTypeMixin:
    object_type = None      # Tên hiển thị: "Sinh viên" / "Giảng viên"
    object_prefix = None    # Prefix dùng để build URL: "sv" / "gv"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_type"] = self.object_type
        context["object_prefix"] = self.object_prefix
        return context

# ----- Base class kế thừa Mixin -----
class BaseListView(ObjectTypeMixin, ListView):
    template_name = "common/list.html"
    context_object_name = "objects"
    
    # các trường filter mặc định là None, override ở subclass
    filter_fields = []  

    def get_queryset(self):
        queryset = super().get_queryset()
        for field in self.filter_fields:
            value = self.request.GET.get(field, "")
            if value:
                kwargs = {f"{field}__icontains": value}
                queryset = queryset.filter(**kwargs)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # giữ giá trị tìm kiếm trong form
        context["filters"] = {field: self.request.GET.get(field, "") for field in self.filter_fields}
        return context    


class BaseDetailView(ObjectTypeMixin, DetailView):
    template_name = "common/detail.html"
    context_object_name = "object"


class BaseCreateView(ObjectTypeMixin, CreateView):
    template_name = "common/form.html"
    form_class = None
    success_url = None


class BaseUpdateView(ObjectTypeMixin, UpdateView):
    template_name = "common/form.html"
    form_class = None
    success_url = None


class BaseDeleteView(ObjectTypeMixin, DeleteView):
    template_name = "common/confirm_delete.html"
    success_url = None


# ----- SINH VIÊN -----
class SVListView(BaseListView):
    model = SV
    object_type = "Sinh viên"
    object_prefix = "sv"
    filter_fields = ["ho_ten", "lop", "khoa"]
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_fields"] = self.filter_fields
        return context

class SVDetailView(BaseDetailView):
    model = SV
    object_type = "Sinh viên"
    object_prefix = "sv"


class SVCreateView(BaseCreateView):
    model = SV
    form_class = SVForm
    object_type = "Sinh viên"
    object_prefix = "sv"
    success_url = reverse_lazy("sv_list")


class SVUpdateView(BaseUpdateView):
    model = SV
    form_class = SVForm
    object_type = "Sinh viên"
    object_prefix = "sv"
    success_url = reverse_lazy("sv_list")


class SVDeleteView(BaseDeleteView):
    model = SV
    object_type = "Sinh viên"
    object_prefix = "sv"
    success_url = reverse_lazy("sv_list")


# ----- GIẢNG VIÊN -----
class GVListView(BaseListView):
    model = GV
    object_type = "Giảng viên"
    object_prefix = "gv"
    filter_fields = ["ho_ten", "bo_mon"]
    def get_queryset(self):
        qs = super().get_queryset()
        ho_ten = self.request.GET.get("ho_ten")
        bo_mon = self.request.GET.get("bo_mon")
        if ho_ten:
            qs = qs.filter(ho_ten__icontains=ho_ten)
        if bo_mon:
            qs = qs.filter(bo_mon_id=bo_mon)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bo_mon_list"] = BoMon.objects.all()
        context["filters"] = {
            "ho_ten": self.request.GET.get("ho_ten", ""),
            "bo_mon": self.request.GET.get("bo_mon", ""),
        }
        context["filter_fields"] = self.filter_fields  # Thêm dòng này
        return context

class GVDetailView(BaseDetailView):
    model = GV
    object_type = "Giảng viên"
    object_prefix = "gv"


class GVCreateView(BaseCreateView):
    model = GV
    form_class = GVForm
    object_type = "Giảng viên"
    object_prefix = "gv"
    success_url = reverse_lazy("gv_list")


class GVUpdateView(BaseUpdateView):
    model = GV
    form_class = GVForm
    object_type = "Giảng viên"
    object_prefix = "gv"
    success_url = reverse_lazy("gv_list")


class GVDeleteView(BaseDeleteView):
    model = GV
    object_type = "Giảng viên"
    object_prefix = "gv"
    success_url = reverse_lazy("gv_list")


from django.shortcuts import render

def csrf_failure(request, reason=""):
    return render(request, "csrf_failure.html", {"reason": reason})


from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomLoginForm

class UserLoginView(LoginView):
    template_name = "user/login.html"
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        # Sinh viên
        if hasattr(user, "sv"):
            return "/user/sv/"
        # Giảng viên
        elif hasattr(user, "gv"):
            return "/user/gv/"
        # Mặc định
        return "/"

class UserLogoutView(LogoutView):
    next_page = "/user/login/"
