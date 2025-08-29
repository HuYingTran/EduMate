from django.shortcuts import render, redirect
from .models import Reflect, Document, Type
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


# -----------------------------
# Tài liệu đào tạo
# -----------------------------
def documents_view(request):
    documents = Document.objects.all().order_by('-id')
    types = Type.objects.all()

    # Lọc
    type_id = request.GET.get('type')
    search_query = request.GET.get('q', '')
    if type_id:
        documents = documents.filter(type_id=type_id)
    if search_query:
        documents = documents.filter(name__icontains=search_query)

    return render(request, 'reflect/documents.html', {
        'documents': documents,
        'types': types,
        'selected_type': type_id,
        'search_query': search_query
    })
    
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Tài liệu đã được tải lên!")
            return redirect('documents_view')
    else:
        form = DocumentForm()

    return render(request, 'reflect/upload_document.html', {'form': form})