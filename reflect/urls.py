# surveys/urls.py
from django.urls import path
from . import views
from .views import ReflectListView, ReflectDetailView, ReflectCreateView, statistics_view

urlpatterns = [
    # ===== Reflects =====
    path('reflects/', ReflectListView.as_view(), name='reflect_list'),
    path('reflects/<int:pk>/', ReflectDetailView.as_view(), name='reflect_detail'),
    path('reflects/create/', ReflectCreateView.as_view(), name='reflect_create'),
    path('reflects/<int:reflect_id>/response/', views.create_response, name='create_response'),
    path('responses/<int:resp_id>/rate/', views.rate_response, name='rate_response'),

    # ===== Documents =====
    path('documents/', views.documents_view, name='documents'),
    path('documents/upload/', views.upload_document, name='upload_document'),

    # ===== Statistics =====
    path('statistics/', statistics_view, name='statistics'),
    
    path('survey', views.survey_list, name='survey_list'),
    path('survey/create/', views.create_survey, name='create_survey'),
    path('survey/take/<int:survey_id>/', views.take_survey, name='take_survey'),
    path('survey/complete/', views.survey_complete, name='survey_complete'),
    path('survey/results/<int:survey_id>/', views.survey_results, name='survey_results'),
    path('survey/<int:survey_id>/edit/', views.edit_survey, name='edit_survey'),
    path("<int:survey_id>/delete/", views.delete_survey, name="delete_survey"),
]
