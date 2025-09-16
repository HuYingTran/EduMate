from django.shortcuts import render, redirect
from .models import Reflect, Document, Type
from .forms import ReflectForm, DocumentForm


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
    if not hasattr(request.user, "sv"):
        return HttpResponseForbidden("Chỉ sinh viên mới được gửi phản ánh.")

    if request.method == "POST":
        form = ReflectForm(request.POST, request.FILES)
        if form.is_valid():
            reflect = form.save(commit=False)
            reflect.student = request.user
            reflect.status = "create"  # đảm bảo
            reflect.save()
            messages.success(request, "Phản ánh của bạn đã được gửi thành công.")
            return redirect("reflect_detail", pk=reflect.pk)
    else:
        form = ReflectForm()

    return render(request, "reflect/reflect_form.html", {"form": form})



from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from datetime import datetime
from .models import Reflect, ReflectResponse
from .forms import ReflectResponseForm

class ReflectListView(LoginRequiredMixin, ListView):
    model = Reflect
    template_name = "reflect/reflect_list.html"
    context_object_name = "reflects"
    paginate_by = 10  # Thêm phân trang
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        
        # Xác định queryset cơ bản theo quyền
        if user.is_staff or user.is_superuser or getattr(user, "is_teacher", False):
            queryset = Reflect.objects.all()
        else:
            queryset = Reflect.objects.filter(student=user)
        
        # Áp dụng các bộ lọc
        queryset = self.apply_filters(queryset)
        
        return queryset.order_by("-created_at")
    
    def apply_filters(self, queryset):
        """Áp dụng các bộ lọc từ request parameters"""
        
        # Bộ lọc tìm kiếm
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(display_student__icontains=search_query)
            )
        
        # Bộ lọc trạng thái
        status_filter = self.request.GET.get('status', '').strip()
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Bộ lọc theo danh mục (nếu có field category)
        category_filter = self.request.GET.get('category', '').strip()
        if category_filter and hasattr(Reflect, 'category'):
            queryset = queryset.filter(category=category_filter)
        
        # Bộ lọc theo mức độ ưu tiên (nếu có field priority)
        priority_filter = self.request.GET.get('priority', '').strip()
        if priority_filter and hasattr(Reflect, 'priority'):
            queryset = queryset.filter(priority=priority_filter)
        
        # Bộ lọc ngày tạo
        date_from = self.request.GET.get('date_from', '').strip()
        date_to = self.request.GET.get('date_to', '').strip()
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from_obj)
            except ValueError:
                pass  # Bỏ qua nếu format ngày không hợp lệ
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to_obj)
            except ValueError:
                pass  # Bỏ qua nếu format ngày không hợp lệ
        
        # Bộ lọc theo sinh viên (chỉ cho giáo viên/admin)
        user = self.request.user
        if (user.is_staff or user.is_superuser or getattr(user, "is_teacher", False)):
            student_filter = self.request.GET.get('student', '').strip()
            if student_filter:
                queryset = queryset.filter(
                    Q(student__username__icontains=student_filter) |
                    Q(student__first_name__icontains=student_filter) |
                    Q(student__last_name__icontains=student_filter) |
                    Q(display_student__icontains=student_filter)
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy queryset để tính thống kê
        full_queryset = self.get_queryset()
        
        # Thống kê trạng thái
        status_counts = full_queryset.values('status').annotate(
            count=Count('status')
        ).order_by('status')
        context['status_counts'] = {item['status']: item['count'] for item in status_counts}
        
        # Thống kê tổng
        context['total_count'] = full_queryset.count()
        
        # Thêm các options cho dropdown filters
        context['status_choices'] = Reflect._meta.get_field('status').choices
        
        # Thêm thông tin về quyền xem
        user = self.request.user
        context['can_view_all'] = (
            user.is_staff or 
            user.is_superuser or 
            getattr(user, "is_teacher", False)
        )
        
        # Thêm danh sách sinh viên cho bộ lọc (chỉ cho giáo viên/admin)
        if context['can_view_all']:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Lấy danh sách sinh viên có phản ánh
            students_with_reflects = Reflect.objects.values_list(
                'student', flat=True
            ).distinct()
            
            context['students_list'] = User.objects.filter(
                id__in=students_with_reflects
            ).order_by('first_name', 'last_name', 'username')
        
        # Thêm các filter parameters hiện tại để maintain state
        filter_params = {}
        for param in ['search', 'status', 'category', 'priority', 'date_from', 'date_to', 'student']:
            value = self.request.GET.get(param, '').strip()
            if value:
                filter_params[param] = value
        context['current_filters'] = filter_params
        
        return context

class ReflectDetailView(DetailView):
    model = Reflect
    template_name = "reflect/reflect_detail.html"
    context_object_name = "reflect"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Danh sách phản hồi của giáo viên
        context["responses"] = self.object.responses.all().order_by("created_at")

        # Form phản hồi (chỉ hiện với giáo viên)
        if self.request.user.is_authenticated and getattr(self.request.user, "is_teacher", False) or self.request.user.is_superuser:
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
            
            reflect.status = "active"
            reflect.save()
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
            
            reflect = resp.reflect
            reflect.status = "done"
            reflect.save()
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

from django.shortcuts import render
from .models import Survey
from chat.models import ChatMessage

@login_required
def home(request):
    chat_history = ChatMessage.objects.filter(user=request.user).order_by("created_at")  # ← Đây
    return render(request, "home.html", {
        "chat_history": chat_history,  # ← Dữ liệu này được truyền vào template
    })
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Survey, Question, Choice, Response, Answer
from .forms import SurveyForm, QuestionFormSet

@login_required
def survey_list(request):
    surveys = Survey.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'reflect/survey_list.html', {'surveys': surveys})

@login_required
def create_survey(request):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        formset = QuestionFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user
            survey.save()
            
            formset.instance = survey
            formset.save()
            
            messages.success(request, 'Survey created successfully!')
            return redirect('survey_list')
    else:
        form = SurveyForm()
        formset = QuestionFormSet()
    
    return render(request, 'reflect/create_survey.html', {'form': form, 'formset': formset})

def take_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, is_active=True)
    
    if request.method == 'POST':
        response = Response.objects.create(survey=survey)
        
        for question in survey.questions.all():
            answer_value = request.POST.get(f'question_{question.id}')
            if answer_value:
                answer = Answer.objects.create(response=response, question=question)
                
                if question.question_type == 'text':
                    answer.text_answer = answer_value
                elif question.question_type == 'choice':
                    answer.choice_answer_id = answer_value
                elif question.question_type == 'rating':
                    answer.rating_answer = int(answer_value)
                
                answer.save()
        
        messages.success(request, 'Thank you for your response!')
        return redirect('survey_list')
    
    return render(request, 'reflect/take_survey.html', {'survey': survey})

def survey_complete(request):
    return render(request, 'reflect/survey_list.html')

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import Survey, Response, Answer

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import Survey, Response, Answer

@login_required
def survey_results(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, created_by=request.user)
    responses = Response.objects.filter(survey=survey).prefetch_related('answers__question')

    # Lọc lấy hỏi đầu tiên
    first_question = survey.questions.first()
    filter_answer = request.GET.get("first_question_answer")

    print(first_question)

    if first_question and filter_answer and filter_answer != "ALL":
        if first_question.question_type == "text":
            responses = responses.filter(
                answers__question=first_question,
                answers__text_answer=filter_answer
            )
        elif first_question.question_type == "choice":
            responses = responses.filter(
                answers__question=first_question,
                answers__choice_answer_id=filter_answer
            )
        elif first_question.question_type == "rating":
            try:
                responses = responses.filter(
                    answers__question=first_question,
                    answers__rating_answer=int(filter_answer)
                )
            except ValueError:
                pass  # nếu filter_answer không phải số

    # Chuẩn bị dữ liệu cho từng câu hỏi
    questions_data = []
    for question in survey.questions.all():
        q_data = {"id": question.id, "text": question.text, "type": question.question_type}

        if question.question_type == "text":
            q_data["text_answers"] = Answer.objects.filter(
                question=question, response__in=responses
            ).exclude(text_answer="")

        elif question.question_type == "choice":
            total = Answer.objects.filter(
                question=question, response__in=responses
            ).exclude(choice_answer=None).count()

            labels, counts, choices = [], [], []
            for choice in question.choices.all():
                count = Answer.objects.filter(
                    question=question, choice_answer=choice, response__in=responses
                ).count()
                percent = round((count / total) * 100, 1) if total > 0 else 0
                choices.append({"text": choice.text, "count": count, "percent": percent})
                labels.append(choice.text)
                counts.append(count)

            q_data.update({"choices": choices, "chart_labels": labels, "chart_counts": counts})

        elif question.question_type == "rating":
            ratings = Answer.objects.filter(question=question, response__in=responses).exclude(rating_answer=None)
            avg_rating = ratings.aggregate(avg=Avg("rating_answer"))["avg"]
            q_data["average_rating"] = round(avg_rating, 1) if avg_rating else None

            breakdown, labels, counts = [], [], []
            total = ratings.count()
            for i in range(5, 0, -1):
                count = ratings.filter(rating_answer=i).count()
                percent = round((count / total) * 100, 1) if total > 0 else 0
                breakdown.append({"stars": i, "count": count, "percent": percent})
                labels.append(f"{i}★")
                counts.append(count)

            q_data.update({"rating_breakdown": breakdown, "chart_labels": labels, "chart_counts": counts})

        questions_data.append(q_data)
        # print(questions_data)

    return render(request, "reflect/survey_result.html", {
            "survey": survey,
            "responses": responses,
            "questions": questions_data,
            "first_question": first_question,
            "rating_choices": [1, 2, 3, 4, 5],  # thêm dòng này`
})


@login_required
def edit_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, created_by=request.user)

    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=survey)
        formset = QuestionFormSet(request.POST, instance=survey)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Survey updated successfully!')
            return redirect('survey_list')
    else:
        form = SurveyForm(instance=survey)
        formset = QuestionFormSet(instance=survey)

    return render(request, 'reflect/edit_survey.html', {
        'form': form,
        'formset': formset,
        'survey': survey
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Survey

def delete_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    if request.method == "POST":
        survey.delete()
        messages.success(request, "Xóa khảo sát thành công.")
        return redirect("survey_list")
    return redirect("survey_list")

@login_required
def change_reflect_status(request, reflect_id):
    reflect = get_object_or_404(Reflect, pk=reflect_id)

    # chỉ cho admin/giáo viên sửa trạng thái
    if not (request.user.is_staff or request.user.is_superuser or getattr(request.user, "is_teacher", False)):
        return HttpResponseForbidden("Bạn không có quyền thay đổi trạng thái.")

    if request.method == "POST":
        new_status = request.POST.get("status")
        valid_choices = [choice[0] for choice in Reflect.STATUS_CHOICES]
        if new_status in valid_choices:
            reflect.status = new_status
            reflect.save()
            messages.success(request, "Cập nhật trạng thái thành công.")
        else:
            messages.error(request, "Trạng thái không hợp lệ.")

    return redirect("reflect_detail", pk=reflect.id)