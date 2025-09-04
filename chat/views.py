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