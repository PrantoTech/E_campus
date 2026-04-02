from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from datetime import date

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


@require_POST
def student_forgot_password(request):
	student_id = request.POST.get('student_id', '').strip().upper()
	dob = request.POST.get('dob', '').strip()
	new_password = request.POST.get('new_password', '')
	confirm_password = request.POST.get('confirm_password', '')

	if not student_id or not dob or not new_password or not confirm_password:
		return JsonResponse({'success': False, 'message': 'Please fill all required fields.'}, status=400)

	if new_password != confirm_password:
		return JsonResponse({'success': False, 'message': 'Passwords do not match.'}, status=400)

	if len(new_password) < 8:
		return JsonResponse({'success': False, 'message': 'Password must be at least 8 characters.'}, status=400)

	try:
		dob_date = date.fromisoformat(dob)
	except ValueError:
		return JsonResponse({'success': False, 'message': 'Enter a valid date of birth.'}, status=400)

	profile = StudentProfile.objects.select_related('user').filter(student_id=student_id, date_of_birth=dob_date).first()
	if profile is None:
		return JsonResponse({'success': False, 'message': 'Student ID and DOB did not match.'}, status=404)

	user = profile.user
	user.set_password(new_password)
	user.save(update_fields=['password'])

	return JsonResponse({
		'success': True,
		'message': 'Password reset successful. Please login with your new password.',
		'email': user.email,
	})


@login_required
def student_dashboard(request):
	profile = getattr(request.user, 'student_profile', None)
	display_name = request.user.get_full_name().strip() or request.user.username
	name_parts = [part[0].upper() for part in display_name.split() if part]
	avatar_text = ''.join(name_parts[:2]) if name_parts else display_name[:2].upper()

	return render(request, 'student_dashboard.html', {
		'profile': profile,
		'display_name': display_name,
		'avatar_text': avatar_text,
	})


@require_POST
@login_required
def upload_profile_photo(request):
	profile = getattr(request.user, 'student_profile', None)
	if profile is None:
		return redirect('/students/dashboard/#profile')

	photo = request.FILES.get('profile_photo')
	if photo is None:
		return redirect('/students/dashboard/#profile')

	content_type = getattr(photo, 'content_type', '') or ''
	if not content_type.startswith('image/'):
		return redirect('/students/dashboard/#profile')

	max_size_bytes = 5 * 1024 * 1024
	if photo.size > max_size_bytes:
		return redirect('/students/dashboard/#profile')

	if profile.profile_photo:
		profile.profile_photo.delete(save=False)

	profile.profile_photo = photo
	profile.save(update_fields=['profile_photo'])
	return redirect('/students/dashboard/#profile')


@require_POST
@login_required
def student_logout(request):
	logout(request)
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		return JsonResponse({'success': True, 'redirect_url': '/'})
	return redirect('/')
