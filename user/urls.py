from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.student_login, name="student_login"),
    
#     # === Sinh viên ===
#     path("sv/register/", views.sv_register, name="sv_register"),
#     path("sv/list/", views.sv_list, name="sv_list"),
#     path("sv/<int:sv_id>/", views.sv_detail, name="sv_detail"),
#     path('sv/<int:pk>/update/<str:status>/', views.sv_update_status, name='sv_update_status'),

#     # === Giáo viên ===
#     path("gv/list/", views.gv_list, name="gv_list"),
#     path("gv/<int:gv_id>/", views.gv_detail, name="gv_detail"),
#     path("gv/<int:gv_id>/approve/", views.gv_approve, name="gv_approve"),
# ]
    # SV URLs
    path('sv/', views.user_list, {'user_type': 'sv'}, name='sv_list'),
    path('sv/register/', views.user_register, {'user_type': 'sv'}, name='sv_register'),
    path('sv/<int:pk>/', views.user_detail_view, {'user_type': 'sv'}, name='sv_detail'),
    path('sv/<int:pk>/update/<str:status>/', views.sv_update_status, name='sv_update_status'),

    # GV URLs
    path('gv/', views.user_list, {'user_type': 'gv'}, name='gv_list'),
    path('gv/register/', views.user_register, {'user_type': 'gv'}, name='gv_register'),
    path('gv/<int:pk>/', views.user_detail_view, {'user_type': 'gv'}, name='gv_detail'),
]
