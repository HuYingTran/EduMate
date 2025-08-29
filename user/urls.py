from django.urls import path
from . import views
from .views import UserLoginView, UserLogoutView

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),

    # Sinh viên
    path('sv/', views.SVListView.as_view(), name='sv_list'),
    path('sv/create/', views.SVCreateView.as_view(), name='sv_create'),
    path('sv/<int:pk>/', views.SVDetailView.as_view(), name='sv_detail'),
    path('sv/<int:pk>/update/', views.SVUpdateView.as_view(), name='sv_update'),
    path('sv/<int:pk>/delete/', views.SVDeleteView.as_view(), name='sv_delete'),

    # Giảng viên
    path('gv/', views.GVListView.as_view(), name='gv_list'),
    path('gv/create/', views.GVCreateView.as_view(), name='gv_create'),
    path('gv/<int:pk>/', views.GVDetailView.as_view(), name='gv_detail'),
    path('gv/<int:pk>/update/', views.GVUpdateView.as_view(), name='gv_update'),
    path('gv/<int:pk>/delete/', views.GVDeleteView.as_view(), name='gv_delete'),
]
