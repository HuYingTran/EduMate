from django.shortcuts import render, redirect
from .models import Reflect
from .forms import ReflectForm

def gui_phan_anh(request):
    if request.method == "POST":
        form = ReflectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("danh_sach")
    else:
        form = ReflectForm()
    return render(request, "reflect/gui.html", {"form": form})

def danh_sach(request):
    phan_anh_list = Reflect.objects.all()
    return render(request, "reflect/danh_sach.html", {"phan_anh_list": phan_anh_list})
