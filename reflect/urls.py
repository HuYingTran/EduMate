from django.urls import path
from . import views
from .views import ReflectListView, ReflectDetailView, ReflectCreateView, statistics_view

urlpatterns = [
    path('reflects/', ReflectListView.as_view(), name='reflect_list'),
    path('reflects/<int:pk>/', ReflectDetailView.as_view(), name='reflect_detail'),
    path('reflects/create/', ReflectCreateView.as_view(), name='reflect_create'),
    
    path("reflects/<int:reflect_id>/response/", views.create_response, name="create_response"),
    path("responses/<int:resp_id>/rate/", views.rate_response, name="rate_response"),
    
    path('documents/', views.documents_view, name='documents'),
    path('documents/upload/', views.upload_document, name='upload_document'),
    
    path("statistics/", statistics_view, name="statistics"),
    
    path('surveys/', views.surveys_view, name='surveys_view'),
    path('surveys/create/', views.create_survey, name='create_survey'),
    path('surveys/<int:survey_id>/edit/', views.edit_survey, name='edit_survey'),
    path('surveys/<int:survey_id>/delete/', views.delete_survey, name='delete_survey'),
]