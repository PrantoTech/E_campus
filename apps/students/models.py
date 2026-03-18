from django.db import models
from django.contrib.auth.models import User


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
	address = models.TextField(blank=True)
	guardian_name = models.CharField(max_length=150)
	guardian_contact = models.CharField(max_length=10)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"
