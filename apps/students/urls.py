from django.urls import path

from . import views

app_name = 'students'

urlpatterns = [
    path('register/', views.register_student, name='register'),
    path('login/', views.student_login, name='login'),
    path('forgot-password/', views.student_forgot_password, name='forgot_password'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('assignments/submit/', views.submit_assignment, name='submit_assignment'),
    path('upload-photo/', views.upload_profile_photo, name='upload_photo'),
    path('logout/', views.student_logout, name='logout'),
]
