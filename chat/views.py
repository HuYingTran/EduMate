from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import re
from .models import ChatSession, ChatMessage, AutoResponse

class ChatService:
    @staticmethod
    def get_auto_response(message):
        """Tìm phản hồi tự động dựa trên từ khóa"""
        message_lower = message.lower()
        
        # Lấy tất cả auto responses đang active
        responses = AutoResponse.objects.filter(is_active=True)
        
        for response in responses:
            keywords = response.get_keywords_list()
            for keyword in keywords:
                if keyword in message_lower:
                    return response.response
        
        # Phản hồi mặc định
        return "Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi sớm nhất có thể."
    
    @staticmethod
    def create_session():
        """Tạo session chat mới"""
        return ChatSession.objects.create()
    
    @staticmethod
    def get_session(session_id):
        """Lấy session theo ID"""
        try:
            return ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            return None

def home(request):
    """Trang chủ với chat widget"""
    return render(request, 'home.html')

@csrf_exempt
@require_http_methods(["POST"])
def start_chat(request):
    """Bắt đầu cuộc trò chuyện mới"""
    try:
        session = ChatService.create_session()
        
        # Tin nhắn chào mừng
        welcome_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content='Xin chào! Tôi có thể hỗ trợ gì cho bạn hôm nay?'
        )
        
        return JsonResponse({
            'status': 'success',
            'session_id': str(session.session_id),
            'welcome_message': {
                'content': welcome_message.content,
                'timestamp': welcome_message.timestamp.isoformat()
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Gửi tin nhắn và nhận phản hồi tự động"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'status': 'error', 'message': 'Tin nhắn không được để trống'})
        
        session = EduChatService.get_session(session_id)
        if not session:
            return JsonResponse({'status': 'error', 'message': 'Session không tồn tại'})
        
        # Lưu tin nhắn của sinh viên
        user_message = ChatMessage.objects.create(
            session=session,
            sender=request.user if request.user.is_authenticated else None,
            message_type='student',
            content=message
        )
        
        # Tạo phản hồi tự động
        auto_response_text, from_kb = EduChatService.get_auto_response(message)
        bot_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=auto_response_text,
            is_auto_response=True
        )
        
        # Nếu không tìm thấy trong KB, thông báo sẽ có giáo viên trả lời
        if not from_kb:
            # Có thể gửi notification cho admin/teacher ở đây
            pass
        
        return JsonResponse({
            'status': 'success',
            'user_message': {
                'content': user_message.content,
                'timestamp': user_message.timestamp.isoformat(),
                'type': 'student'
            },
            'bot_message': {
                'content': bot_message.content,
                'timestamp': bot_message.timestamp.isoformat(),
                'type': 'bot',
                'from_knowledge_base': from_kb
            }
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_http_methods(["GET"])
def get_chat_history(request, session_id):
    """Lấy lịch sử chat"""
    try:
        session = ChatService.get_session(session_id)
        if not session:
            return JsonResponse({'status': 'error', 'message': 'Session không tồn tại'})
        
        messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
        messages_data = []
        
        for message in messages:
            messages_data.append({
                'type': message.message_type,
                'content': message.content,
                'timestamp': message.timestamp.isoformat()
            })
        
        return JsonResponse({
            'status': 'success',
            'messages': messages_data
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def save_user_info(request):
    """Lưu thông tin user"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        user_name = data.get('name', '')
        user_email = data.get('email', '')
        user_phone = data.get('phone', '')
        
        session = ChatService.get_session(session_id)
        if not session:
            return JsonResponse({'status': 'error', 'message': 'Session không tồn tại'})
        
        session.user_name = user_name
        session.user_email = user_email  
        session.user_phone = user_phone
        session.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
