from django.urls import path
from . import views

urlpatterns = [
    path("gui/", views.gui_phan_anh, name="gui_phan_anh"),
    path("danh-sach/", views.danh_sach, name="danh_sach"),
    
    path('documents/', views.documents_view, name='documents'),
    path('documents/upload/', views.upload_document, name='upload_document'),
]
