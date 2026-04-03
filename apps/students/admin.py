from django.contrib import admin
from .models import AcademicCalendarEvent, FeeStructure, StudentAssignment, StudentAssignmentSubmission, StudentAttendance, StudentFeePayment, StudentProfile


admin.site.site_header = 'E-Campus Admin'
admin.site.site_title = 'E-Campus Admin Portal'
admin.site.index_title = 'Campus Operations'


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
	list_display = ('student_id', 'user', 'roll_no', 'course', 'semester', 'advisor_faculty', 'overall_gpa', 'mobile', 'created_at')
	list_filter = ('course', 'semester', 'gender', 'created_at')
	search_fields = ('student_id', 'user__username', 'user__first_name', 'user__email', 'roll_no', 'advisor_faculty__faculty_id', 'advisor_faculty__user__first_name')


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
	list_display = ('student', 'attendance_date', 'is_present', 'updated_at')
	list_filter = ('is_present', 'attendance_date', 'student__course', 'student__semester')
	search_fields = ('student__student_id', 'student__user__first_name', 'student__user__email')
	ordering = ('-attendance_date', '-updated_at')


@admin.register(AcademicCalendarEvent)
class AcademicCalendarEventAdmin(admin.ModelAdmin):
	list_display = ('title', 'event_date', 'event_type', 'visibility', 'venue', 'is_active')
	list_filter = ('event_type', 'visibility', 'is_active', 'event_date')
	search_fields = ('title', 'description', 'venue')
	ordering = ('event_date', 'title')


@admin.register(StudentAssignment)
class StudentAssignmentAdmin(admin.ModelAdmin):
	list_display = ('title', 'course', 'semester', 'due_date', 'is_active', 'posted_by')
	list_filter = ('course', 'semester', 'is_active', 'due_date')
	search_fields = ('title', 'description', 'course', 'semester')
	ordering = ('due_date', '-created_at')


@admin.register(StudentAssignmentSubmission)
class StudentAssignmentSubmissionAdmin(admin.ModelAdmin):
	list_display = ('assignment', 'student', 'status', 'marks', 'submitted_at', 'reviewed_by')
	list_filter = ('status', 'assignment__course', 'assignment__semester', 'submitted_at')
	search_fields = ('assignment__title', 'student__student_id', 'student__user__first_name', 'feedback')
	ordering = ('-submitted_at',)


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
	list_display = ('course', 'semester', 'academic_year', 'total_fee', 'due_date', 'is_active')
	list_filter = ('course', 'semester', 'academic_year', 'is_active')
	search_fields = ('course', 'semester', 'academic_year', 'title', 'description')
	ordering = ('course', 'semester', 'academic_year')


@admin.register(StudentFeePayment)
class StudentFeePaymentAdmin(admin.ModelAdmin):
	list_display = ('receipt_no', 'student', 'fee_structure', 'amount_paid', 'payment_date', 'payment_mode')
	list_filter = ('payment_mode', 'payment_date', 'fee_structure__course', 'fee_structure__semester', 'fee_structure__academic_year')
	search_fields = ('receipt_no', 'student__student_id', 'student__user__first_name')
	ordering = ('-payment_date', '-created_at')
