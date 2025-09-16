import json
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatMessage
from reflect.models import Survey  # nếu bạn có app khảo sát

# ---------------- Chat API ----------------
@login_required
@csrf_exempt
def chat_send(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"reply": "⚠️ Dữ liệu không hợp lệ."})

        msg = data.get("message", "").strip()

        if not msg:
            return JsonResponse({"reply": "⚠️ Bạn chưa nhập tin nhắn."})

        # 1. Tìm câu hỏi tương tự trong DB
        existing = ChatMessage.objects.filter(question__icontains=msg, answer__isnull=False).first()
        if existing:
            return JsonResponse({"reply": existing.answer})

        # 2. Nếu chưa có, lưu lại để GV/Admin vào trả lời
        ChatMessage.objects.create(user=request.user, question=msg)

        return JsonResponse({"reply": "❓ Câu hỏi của bạn đã được ghi nhận. Giáo viên sẽ trả lời sớm nhất có thể."})

    return JsonResponse({"reply": "⚠️ Chỉ hỗ trợ phương thức POST."})

# ---------------- Check quyền GV/Admin ----------------
def is_teacher_or_admin(user):
    return user.is_superuser or hasattr(user, "gv")

# ---------------- Trang quản lý câu hỏi chưa trả lời ----------------
@login_required
@user_passes_test(is_teacher_or_admin)
def unanswered_questions(request):
    unanswered = ChatMessage.objects.filter(answer__isnull=True).order_by("-created_at")
    answered = ChatMessage.objects.filter(answer__isnull=False).order_by("-created_at")
    return render(request, "chat/unanswered_list.html", {
        "unanswered": unanswered,
        "answered": answered,
    })

@login_required
@user_passes_test(is_teacher_or_admin)
def answer_question(request, pk):
    question = get_object_or_404(ChatMessage, pk=pk)
    if request.method == "POST":
        answer = request.POST.get("answer")
        if answer:
            question.answer = answer
            question.save()
            return redirect("unanswered_questions")
    return render(request, "chat/answer_form.html", {"question": question})


@login_required
def get_chat_history(request):
    if request.method == "GET":
        messages = ChatMessage.objects.filter(
            user=request.user
        ).order_by("created_at")
        
        history = []
        for msg in messages:
            history.append({
                'question': msg.question,
                'answer': msg.answer,
                'created_at': msg.created_at.strftime('%d/%m/%Y %H:%M')
            })
        
        return JsonResponse({'history': history})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q
from .models import ChatMessage  # hoặc model lưu câu hỏi

@require_GET
def chat_suggestions(request):
    query = request.GET.get('q', '').strip()
    suggestions = []
    if query:
        # Lọc các câu hỏi bắt đầu hoặc chứa query, loại bỏ trùng
        qs = ChatMessage.objects.filter(
            question__icontains=query
        ).values_list('question', flat=True).distinct()[:5]  # tối đa 5 gợi ý
        suggestions = list(qs)
    return JsonResponse({'suggestions': suggestions})

import openpyxl
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.models import User
from .models import ChatMessage

@login_required
@user_passes_test(is_teacher_or_admin)
def import_qna_excel(request):
    if request.method == "POST" and request.FILES.get("excel_file"):
        excel_file = request.FILES["excel_file"]

        try:
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active

            # Giả sử cột Excel: Username | Question | Answer
            rows = list(ws.iter_rows(min_row=2, values_only=True))
            imported = 0

            for row in rows:
                username, question, answer = row[0], row[1], row[2] if len(row) > 2 else None

                if not question:
                    continue

                # Nếu không có username thì gán user=None
                user = None
                if username:
                    user, _ = User.objects.get_or_create(username=username)

                ChatMessage.objects.create(
                    user=user,
                    question=question,
                    answer=answer if answer else None
                )
                imported += 1

            messages.success(request, f"✅ Đã import {imported} câu hỏi/trả lời từ Excel.")
        except Exception as e:
            messages.error(request, f"⚠️ Lỗi khi import file: {e}")

    return redirect("unanswered_questions")  # quay lại trang quản lý
