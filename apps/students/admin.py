from django.contrib import admin
from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ('student_id', 'user', 'roll_no', 'course', 'semester', 'mobile', 'created_at')
	list_filter = ('course', 'semester', 'gender', 'created_at')
	search_fields = ('student_id', 'user__username', 'user__first_name', 'user__email', 'roll_no')
