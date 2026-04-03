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
    path('assignments/create/', views.create_assignment, name='create_assignment'),
    path('assignments/delete/', views.delete_assignment, name='delete_assignment'),
    path('assignments/review/', views.review_assignment_submission, name='review_assignment_submission'),
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('announcements/delete/', views.delete_announcement, name='delete_announcement'),
    path('upload-photo/', views.upload_profile_photo, name='upload_photo'),
    path('logout/', views.faculty_logout, name='logout'),
]
