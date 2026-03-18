from django.urls import path

from . import views

app_name = 'students'

urlpatterns = [
    path('register/', views.register_student, name='register'),
    path('login/', views.student_login, name='login'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('logout/', views.student_logout, name='logout'),
]
