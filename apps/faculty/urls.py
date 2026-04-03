from django.urls import path

from . import views

app_name = 'faculty'

urlpatterns = [
    path('login/', views.faculty_login, name='login'),
    path('forgot-password/', views.faculty_forgot_password, name='forgot_password'),
    path('dashboard/', views.faculty_dashboard, name='dashboard'),
    path('attendance/mark/', views.mark_student_attendance, name='mark_student_attendance'),
    path('students/update/', views.update_student_details, name='update_student_details'),
    path('faculty/update/', views.update_faculty_details, name='update_faculty_details'),
    path('upload-photo/', views.upload_profile_photo, name='upload_photo'),
    path('logout/', views.faculty_logout, name='logout'),
]
