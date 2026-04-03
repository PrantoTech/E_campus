import os

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def student_profile_photo_upload_to(instance, filename):
	_, extension = os.path.splitext(filename or '')
	extension = extension.lower() or '.jpg'
	student_id = (instance.student_id or f'user-{instance.user_id or "new"}').strip().upper()
	timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
	return f"students/profile_photos/student_{student_id}_{timestamp}{extension}"


class StudentProfile(models.Model):
	GENDER_CHOICES = [
		('Male', 'Male'),
		('Female', 'Female'),
		('Other', 'Other'),
	]

	COURSE_CHOICES = [
		('DCST', 'DCST'),
		('DME', 'DME'),
		('DCE', 'DCE'),
		('DSE', 'DSE'),
		('DCFS', 'DCFS'),
		('DETC', 'DETC'),
		('DEE', 'DEE'),
	]

	SEMESTER_CHOICES = [(str(number), str(number)) for number in range(1, 7)]

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
	student_id = models.CharField(max_length=20, unique=True)
	date_of_birth = models.DateField()
	gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
	mobile = models.CharField(max_length=10)
	roll_no = models.PositiveIntegerField(unique=True)
	course = models.CharField(max_length=10, choices=COURSE_CHOICES)
	semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)
	advisor_faculty = models.ForeignKey('faculty.FacultyProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='advised_students')
	overall_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
	address = models.TextField(blank=True)
	guardian_name = models.CharField(max_length=150)
	guardian_contact = models.CharField(max_length=10)
	profile_photo = models.ImageField(upload_to=student_profile_photo_upload_to, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"

	def save(self, *args, **kwargs):
		old_photo_name = None
		if self.pk:
			old_photo_name = type(self).objects.filter(pk=self.pk).values_list('profile_photo', flat=True).first()

		super().save(*args, **kwargs)

		new_photo_name = self.profile_photo.name if self.profile_photo else None
		if old_photo_name and old_photo_name != new_photo_name:
			self.profile_photo.storage.delete(old_photo_name)

	def delete(self, *args, **kwargs):
		photo_name = self.profile_photo.name if self.profile_photo else None
		super().delete(*args, **kwargs)
		if photo_name:
			self.profile_photo.storage.delete(photo_name)


class StudentAttendance(models.Model):
	student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
	attendance_date = models.DateField()
	is_present = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-attendance_date', '-updated_at']
		constraints = [
			models.UniqueConstraint(fields=['student', 'attendance_date'], name='unique_student_attendance_per_day'),
		]

	def __str__(self):
		status = 'Present' if self.is_present else 'Absent'
		return f"{self.student.student_id} - {self.attendance_date} - {status}"


class AcademicCalendarEvent(models.Model):
	EVENT_TYPE_CHOICES = [
		('Event', 'Event'),
		('Holiday', 'Holiday'),
		('Exam', 'Exam'),
		('Notice', 'Notice'),
	]

	title = models.CharField(max_length=200)
	event_date = models.DateField()
	event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='Event')
	description = models.TextField(blank=True)
	venue = models.CharField(max_length=200, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['event_date', 'title']

	def __str__(self):
		return f"{self.event_date} - {self.title}"


class FeeStructure(models.Model):
	course = models.CharField(max_length=10, choices=StudentProfile.COURSE_CHOICES)
	semester = models.CharField(max_length=1, choices=StudentProfile.SEMESTER_CHOICES)
	academic_year = models.CharField(max_length=9)
	total_fee = models.DecimalField(max_digits=10, decimal_places=2)
	due_date = models.DateField()
	title = models.CharField(max_length=200, blank=True)
	description = models.TextField(blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['course', 'semester', 'academic_year']
		constraints = [
			models.UniqueConstraint(fields=['course', 'semester', 'academic_year'], name='unique_fee_structure_per_course_semester_year'),
		]

	def __str__(self):
		return f"{self.course} Semester {self.semester} - {self.academic_year}"


class StudentFeePayment(models.Model):
	PAYMENT_MODE_CHOICES = [
		('Cash', 'Cash'),
		('Card', 'Card'),
		('UPI', 'UPI'),
		('Net Banking', 'Net Banking'),
		('Bank Transfer', 'Bank Transfer'),
	]

	student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='fee_payments')
	fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='payments')
	amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
	payment_date = models.DateField()
	payment_mode = models.CharField(max_length=30, choices=PAYMENT_MODE_CHOICES)
	receipt_no = models.CharField(max_length=50, unique=True)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-payment_date', '-created_at']

	def __str__(self):
		return f"{self.receipt_no} - {self.student.student_id} - {self.amount_paid}"
