from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

from .models import SV, GV
from .forms import UserSVRegistrationForm, GVRegistrationForm, StudentLoginForm


# ================== LIST ================== #
@staff_member_required
def user_list(request, user_type):
    if user_type == "sv":
        users = SV.objects.all()
    else:
        users = GV.objects.all()
    return render(request, "user/user_list.html", {"users": users, "user_type": user_type.upper()})


# ================== DETAIL ================== #
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import SV, GV

@staff_member_required
def user_detail_view(request, user_type, pk):
    """
    Hiển thị thông tin chi tiết SV hoặc GV
    user_type: 'sv' hoặc 'gv'
    """
    user_type_lower = user_type.lower()
    
    if user_type_lower == "sv":
        user_obj = get_object_or_404(SV, id=pk)
    else:
        user_obj = get_object_or_404(GV, id=pk)

    # Cập nhật trạng thái nếu POST và admin
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(user_obj.STATUS_CHOICES).keys():
            user_obj.status = new_status
            user_obj.save()
            messages.success(request, f"✅ Trạng thái của {user_obj.ho_ten} đã được cập nhật.")
        return redirect("user_detail", user_type=user_type, pk=pk)

    return render(request, "user/user_detail.html", {
        "user_obj": user_obj,
        "user_type": user_type_upper(user_type_lower),
    })


def user_type_upper(user_type_lower):
    """Trả về chữ hoa cho hiển thị: 'SV' hoặc 'GV'"""
    return "SV" if user_type_lower == "sv" else "GV"


# ================== REGISTER ================== #
def user_register(request, user_type):
    if user_type == "sv":
        form_class = UserSVRegistrationForm
    else:
        form_class = GVRegistrationForm

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            user = form.save()
            if user_type == "sv":
                SV.objects.create(
                    user=user,
                    ho_ten=form.cleaned_data["ho_ten"],
                    ngay_sinh=form.cleaned_data["ngay_sinh"],
                    gioi_tinh=form.cleaned_data["gioi_tinh"],
                    email=form.cleaned_data.get("email"),
                )
            else:
                GV.objects.create(
                    user=user,
                    ho_ten=form.cleaned_data["ho_ten"],
                    email=form.cleaned_data.get("email"),
                )
            login(request, user)
            return redirect("home")
    else:
        form = form_class()
    return render(request, "user/user_register.html", {"form": form, "user_type": user_type.upper()})


# ================== STUDENT LOGIN ================== #
def student_login(request):
    if request.method == "POST":
        form = StudentLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = StudentLoginForm()
    return render(request, "login.html", {"form": form})


# ================== CSRF ================== #
def csrf_failure(request, reason=""):
    return render(request, "csrf_failure.html", {"reason": reason}, status=403)


# ================== SV UPDATE STATUS ================== #
@staff_member_required
def sv_update_status(request, pk, status):
    sv = get_object_or_404(SV, pk=pk)
    sv.status = status
    sv.save()
    return redirect("sv_detail", pk=pk)
