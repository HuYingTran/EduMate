from django.shortcuts import render, redirect
from .models import Reflect, Document, Type
from .forms import ReflectForm, DocumentForm

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
            return redirect('documents')
    else:
        form = DocumentForm()

    return render(request, 'reflect/update_document.html', {'form': form})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Reflect
from .forms import ReflectForm, ReflectResponseForm

from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import Reflect
from .forms import ReflectForm

class ReflectCreateView(CreateView):
    model = Reflect
    form_class = ReflectForm
    template_name = "reflect/reflect_form.html"
    success_url = reverse_lazy("reflect_list")

    def form_valid(self, form):
        # Gán người tạo là user hiện tại
        form.instance.student = self.request.user
        return super().form_valid(form)

# Sinh viên tạo phản ánh
@login_required
def create_reflect(request):
    if request.method == "POST":
        form = ReflectForm(request.POST, request.FILES)
        if form.is_valid():
            reflect = form.save(commit=False)
            reflect.student = request.user
            reflect.save()
            return redirect("reflect_list")  # hoặc trang chi tiết phản ánh
    else:
        form = ReflectForm()
    return render(request, "reflect/reflect_form.html", {"form": form})


# Giáo viên phản hồi phản ánh
@login_required
def add_response(request, reflect_id):
    reflect = get_object_or_404(Reflect, id=reflect_id)
    if request.method == "POST":
        form = ReflectResponseForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.reflect = reflect
            response.teacher = request.user
            response.save()
            return redirect("reflect_detail", pk=reflect.id)
    else:
        form = ReflectResponseForm()
    return render(request, "reflect/response_form.html", {"form": form, "reflect": reflect})


from django.views.generic import ListView
from .models import Reflect

class ReflectListView(ListView):
    model = Reflect
    template_name = "reflect/reflect_list.html"
    context_object_name = "reflects"
    ordering = ["-created_at"]  # mới nhất lên đầu

from django.views.generic import DetailView
from .models import Reflect, ReflectResponse

from django.views.generic import DetailView
from .models import Reflect, ReflectResponse
from .forms import ReflectResponseForm

class ReflectDetailView(DetailView):
    model = Reflect
    template_name = "reflect/reflect_detail.html"
    context_object_name = "reflect"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Danh sách phản hồi
        context["responses"] = self.object.responses.all().order_by("created_at")
        # Form để giáo viên gửi phản hồi mới
        if self.request.user.is_authenticated and hasattr(self.request.user, 'is_teacher') and self.request.user.is_teacher:
            context["form"] = ReflectResponseForm()
        return context



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Reflect
from .forms import ReflectResponseForm

@login_required
def create_response(request, reflect_id):
    reflect = get_object_or_404(Reflect, pk=reflect_id)

    if request.method == "POST":
        form = ReflectResponseForm(request.POST, request.FILES)
        if form.is_valid():
            response = form.save(commit=False)
            response.reflect = reflect
            response.teacher = request.user
            response.save()
            return redirect("reflect_detail", pk=reflect.id)
    else:
        form = ReflectResponseForm()

    return render(request, "reflect/response_form.html", {"form": form, "reflect": reflect})


@login_required
def rate_response(request, resp_id):
    resp = get_object_or_404(ReflectResponse, pk=resp_id)
    if request.user != resp.reflect.student:
        return HttpResponseForbidden("Chỉ sinh viên của phản ánh mới được đánh giá phản hồi.")
    if request.method == "POST":
        rating = int(request.POST.get("rating", 0))
        if 1 <= rating <= 5:
            resp.rating = rating
            resp.save()
    return redirect("reflect_detail", pk=resp.reflect.id)


from django.db.models import Count, Avg
from django.shortcuts import render
from .models import Reflect, ReflectResponse, Type
from django.db.models import Count, Avg, Value, FloatField
from django.db.models.functions import Coalesce

from datetime import timedelta
from django.db.models import Count, Avg, IntegerField, FloatField, Q, Value
from django.db.models.functions import Coalesce, TruncMonth
from django.utils.timezone import now
from django.shortcuts import render


def statistics_view(request):
    # Lấy tháng từ request, nếu không có thì lấy tháng hiện tại
    selected_month = request.GET.get("month")
    if selected_month:
        year, month = map(int, selected_month.split("-"))
        first_day = now().replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        first_day = now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    next_month = (first_day + timedelta(days=32)).replace(day=1)
    current_month = first_day.strftime("%Y-%m")

    # Số lượng phản ánh theo Type (lọc theo tháng)
    reflect_by_type = (
        Type.objects.annotate(
            total_reflects=Count(
                "reflects",
                filter=Q(reflects__created_at__gte=first_day, reflects__created_at__lt=next_month)
            )
        )
        .values("name_type", "total_reflects")
    )

    # Rating trung bình theo Type (lọc theo tháng)
    rating_by_type = (
        Type.objects.annotate(
            avg_rating=Coalesce(
                Avg(
                    "reflects__responses__rating",
                    filter=Q(reflects__created_at__gte=first_day, reflects__created_at__lt=next_month),
                ),
                Value(0.0),
                output_field=FloatField(),
            )
        )
        .values("name_type", "avg_rating")
    )

    # Xu hướng phản ánh theo tháng (toàn bộ, không lọc để giữ biểu đồ trend)
    reflects_by_month = (
        Reflect.objects.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )
    reflects_by_month_list = [
        {"month": r["month"].strftime("%Y-%m"), "total": r["total"]}
        for r in reflects_by_month
    ]

    # Biểu đồ quạt: tỷ lệ phản ánh trong tháng đã chọn
    reflects_pie_month = (
        Type.objects.annotate(
            total_in_month=Count(
                "reflects",
                filter=Q(reflects__created_at__gte=first_day, reflects__created_at__lt=next_month),
            )
        )
        .values("name_type", "total_in_month")
    )

    context = {
        "reflect_by_type": list(reflect_by_type),
        "rating_by_type": list(rating_by_type),
        "reflects_by_month": reflects_by_month_list,
        "reflects_pie_month": list(reflects_pie_month),
        "current_month": current_month,
    }
    return render(request, "reflect/statistics.html", context)


from django.shortcuts import render, get_object_or_404, redirect
from .models import Survey
from .forms import SurveyForm

# Danh sách Survey
def surveys_view(request):
    surveys = Survey.objects.all().order_by('-created_at')
    return render(request, 'reflect/surveys.html', {'surveys': surveys})

# Tạo Survey mới
def create_survey(request):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('surveys_view')
    else:
        form = SurveyForm()
    return render(request, 'reflect/update_survey.html', {'form': form, 'title': 'Tạo khảo sát mới'})

# Sửa Survey
def edit_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=survey)
        if form.is_valid():
            form.save()
            return redirect('surveys_view')
    else:
        form = SurveyForm(instance=survey)
    return render(request, 'reflect/update_survey.html', {'form': form, 'title': 'Sửa khảo sát'})

# Xóa Survey
def delete_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    if request.method == 'POST':
        survey.delete()
        return redirect('surveys_view')
    return render(request, 'reflect/delete_survey.html', {'survey': survey})
