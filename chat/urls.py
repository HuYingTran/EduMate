from django.urls import path
from . import views

urlpatterns = [
    path("send/", views.chat_send, name="chat_send"),
    path("unanswered/", views.unanswered_questions, name="unanswered_questions"),
    path("answer/<int:pk>/", views.answer_question, name="answer_question"),
    path('api/chat/history/', views.get_chat_history, name='get_chat_history'),
    path('suggestions/', views.chat_suggestions, name='chat_suggestions'),
    path("import-qna-excel/", views.import_qna_excel, name="import_qna_excel"),
]
