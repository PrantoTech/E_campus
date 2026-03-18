from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import StudentProfile


def _generate_student_id(roll_no: int) -> str:
	base_student_id = f"TPI{roll_no}"
	candidate = base_student_id
	counter = 1
	while StudentProfile.objects.filter(student_id=candidate).exists():
		candidate = f"{base_student_id}-{counter}"
		counter += 1
	return candidate


@require_POST
@transaction.atomic
def register_student(request):
	name = request.POST.get('name', '').strip()
	dob = request.POST.get('dob', '').strip()
	gender = request.POST.get('gender', '').strip()
	email = request.POST.get('email', '').strip().lower()
	mobile = request.POST.get('mobile', '').strip()
	password = request.POST.get('password', '')
	confirm_password = request.POST.get('confirm_password', '')
	roll_no = request.POST.get('roll_no', '').strip()
	course = request.POST.get('course', '').strip()
	semester = request.POST.get('semester', '').strip()
	address = request.POST.get('address', '').strip()
	guardian_name = request.POST.get('guardian_name', '').strip()
	guardian_contact = request.POST.get('guardian_contact', '').strip()

	required_values = [name, dob, gender, email, mobile, password, confirm_password, roll_no, course, semester, guardian_name, guardian_contact]
	if any(not value for value in required_values):
		return JsonResponse({'success': False, 'message': 'Please fill all required fields.'}, status=400)

	if password != confirm_password:
		return JsonResponse({'success': False, 'message': 'Passwords do not match.'}, status=400)

	if User.objects.filter(email=email).exists():
		return JsonResponse({'success': False, 'message': 'An account with this email already exists.'}, status=400)

	if StudentProfile.objects.filter(roll_no=roll_no).exists():
		return JsonResponse({'success': False, 'message': 'This roll number is already registered.'}, status=400)

	try:
		roll_no_int = int(roll_no)
	except ValueError:
		return JsonResponse({'success': False, 'message': 'Roll number must be numeric.'}, status=400)

	student_id = _generate_student_id(roll_no_int)

	user = User.objects.create_user(
		username=email,
		email=email,
		password=password,
		first_name=name,
	)

	StudentProfile.objects.create(
		user=user,
		student_id=student_id,
		date_of_birth=dob,
		gender=gender,
		mobile=mobile,
		roll_no=roll_no_int,
		course=course,
		semester=semester,
		address=address,
		guardian_name=guardian_name,
		guardian_contact=guardian_contact,
	)

	return JsonResponse({
		'success': True,
		'message': 'Registration successful.',
		'student_id': student_id,
		'username': email,
	})


@require_POST
def student_login(request):
	email = request.POST.get('email', '').strip().lower()
	password = request.POST.get('password', '')

	if not email or not password:
		return JsonResponse({'success': False, 'message': 'Email and password are required.'}, status=400)

	user = authenticate(request, username=email, password=password)
	if user is None:
		return JsonResponse({'success': False, 'message': 'Invalid student credentials.'}, status=401)

	if not hasattr(user, 'student_profile'):
		return JsonResponse({'success': False, 'message': 'This account is not a student account.'}, status=403)

	login(request, user)
	return JsonResponse({'success': True, 'redirect_url': '/students/dashboard/'})


@login_required
def student_dashboard(request):
	if not hasattr(request.user, 'student_profile'):
		return render(request, 'students/dashboard.html', {'profile': None})

	return render(request, 'students/dashboard.html', {'profile': request.user.student_profile})


@require_POST
@login_required
def student_logout(request):
	logout(request)
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		return JsonResponse({'success': True, 'redirect_url': '/'})
	return redirect('/')
