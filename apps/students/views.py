import calendar as pycalendar
from datetime import date
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Case, Count, IntegerField, Sum, When
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import AcademicCalendarEvent, FeeStructure, StudentAssignment, StudentAssignmentSubmission, StudentAttendance, StudentFeePayment, StudentProfile


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
		'login_id': user.email,
	})


@login_required
def student_dashboard(request):
	profile = getattr(request.user, 'student_profile', None)
	display_name = request.user.get_full_name().strip() or request.user.username
	name_parts = [part[0].upper() for part in display_name.split() if part]
	avatar_text = ''.join(name_parts[:2]) if name_parts else display_name[:2].upper()

	today = date.today()
	selected_month_value = request.GET.get('month', '').strip()
	selected_year = today.year
	selected_month_number = today.month
	if selected_month_value:
		try:
			month_year, month_no = selected_month_value.split('-', 1)
			candidate_year = int(month_year)
			candidate_month = int(month_no)
			if 1 <= candidate_month <= 12:
				selected_year = candidate_year
				selected_month_number = candidate_month
		except (TypeError, ValueError):
			pass

	selected_month = f'{selected_year:04d}-{selected_month_number:02d}'
	selected_month_label = date(selected_year, selected_month_number, 1).strftime('%B %Y')
	calendar_weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
	month_first_weekday, month_total_days = pycalendar.monthrange(selected_year, selected_month_number)

	month_events_qs = AcademicCalendarEvent.objects.filter(
		is_active=True,
		visibility='ALL',
		event_date__year=selected_year,
		event_date__month=selected_month_number,
	).exclude(
		event_type='Meeting',
	).order_by('event_date', 'title')

	upcoming_events_qs = AcademicCalendarEvent.objects.filter(
		is_active=True,
		visibility='ALL',
		event_date__gte=today,
	).exclude(
		event_type='Meeting',
	).order_by('event_date', 'title')

	event_badge_map = {
		'Event': 'blue',
		'Holiday': 'pink',
		'Exam': 'green',
		'Notice': 'yellow',
	}

	month_event_dates = set(month_events_qs.values_list('event_date', flat=True))
	calendar_cells = []
	for _ in range(month_first_weekday):
		calendar_cells.append({'is_empty': True, 'day_number': '', 'is_today': False, 'has_event': False})

	for day_number in range(1, month_total_days + 1):
		cell_date = date(selected_year, selected_month_number, day_number)
		calendar_cells.append({
			'is_empty': False,
			'day_number': day_number,
			'is_today': cell_date == today,
			'has_event': cell_date in month_event_dates,
		})

	while len(calendar_cells) % 7 != 0:
		calendar_cells.append({'is_empty': True, 'day_number': '', 'is_today': False, 'has_event': False})

	calendar_upcoming_dates = [
		{
			'title': item.title,
			'event_type': item.event_type,
			'event_date': item.event_date,
			'description': item.description,
		}
		for item in upcoming_events_qs[:4]
	]

	calendar_month_events = [
		{
			'title': item.title,
			'event_type': item.event_type,
			'badge_class': event_badge_map.get(item.event_type, 'blue'),
			'event_date': item.event_date,
			'description': item.description,
			'venue': item.venue,
		}
		for item in month_events_qs
	]

	attendance_overall_percentage = 0.0
	attendance_total_classes = 0
	attendance_present_classes = 0
	attendance_absent_classes = 0
	monthly_overall_percentage = 0.0
	monthly_total_classes = 0
	monthly_present_classes = 0
	monthly_absent_classes = 0
	attendance_monthly_rows = []
	fee_current_structure = None
	fee_structures = []
	fee_payment_rows = []
	fee_receipts = []
	fee_recent_payment = None
	assignment_rows = []
	fee_summary = {
		'current_semester_label': '-',
		'current_fee': 0,
		'paid_total': 0,
		'pending_balance': 0,
		'clearance_percentage': 0.0,
		'annual_total': 0,
		'payment_mode': '-',
		'due_date': None,
		'current_due_message': 'No fee structure available.',
		'paid_semesters': 0,
		'total_semesters': 0,
	}

	if profile is not None:
		assignment_rows = list(StudentAssignment.objects.filter(
			is_active=True,
			course=profile.course,
			semester=profile.semester,
		).order_by('due_date', '-created_at')[:8])
		assignment_ids = [item.id for item in assignment_rows]
		submission_map = {
			entry.assignment_id: entry
			for entry in StudentAssignmentSubmission.objects.filter(student=profile, assignment_id__in=assignment_ids)
		}
		assignment_rows = [
			{
				'assignment': item,
				'submission': submission_map.get(item.id),
			}
			for item in assignment_rows
		]

		attendance_qs = StudentAttendance.objects.filter(student=profile)
		attendance_total_classes = attendance_qs.count()
		attendance_present_classes = attendance_qs.filter(is_present=True).count()
		attendance_absent_classes = max(attendance_total_classes - attendance_present_classes, 0)
		attendance_overall_percentage = round((attendance_present_classes * 100.0 / attendance_total_classes), 1) if attendance_total_classes else 0.0

		monthly_qs = attendance_qs.filter(attendance_date__year=selected_year, attendance_date__month=selected_month_number)
		monthly_total_classes = monthly_qs.count()
		monthly_present_classes = monthly_qs.filter(is_present=True).count()
		monthly_absent_classes = max(monthly_total_classes - monthly_present_classes, 0)
		monthly_overall_percentage = round((monthly_present_classes * 100.0 / monthly_total_classes), 1) if monthly_total_classes else 0.0

		monthly_history = attendance_qs.annotate(month=TruncMonth('attendance_date')).values('month').annotate(
			total=Count('id'),
			present=Sum(Case(When(is_present=True, then=1), default=0, output_field=IntegerField())),
		).order_by('-month')[:6]

		for item in monthly_history:
			total = item['total']
			present = item['present'] or 0
			absent = max(total - present, 0)
			percentage = round((present * 100.0 / total), 1) if total else 0.0
			attendance_monthly_rows.append({
				'month_label': item['month'].strftime('%B %Y') if item['month'] else '-',
				'total': total,
				'present': present,
				'absent': absent,
				'percentage': percentage,
			})

		fee_structures_qs = FeeStructure.objects.filter(course=profile.course, is_active=True).order_by('semester', 'academic_year')
		fee_structures = list(fee_structures_qs)
		fee_payment_qs = StudentFeePayment.objects.select_related('fee_structure').filter(student=profile, fee_structure__course=profile.course)

		fee_payment_map = {}
		for payment in fee_payment_qs:
			structure_id = payment.fee_structure_id
			fee_payment_map.setdefault(structure_id, {'paid_total': 0, 'latest_mode': payment.payment_mode, 'latest_date': payment.payment_date})
			fee_payment_map[structure_id]['paid_total'] += payment.amount_paid
			if payment.payment_date >= fee_payment_map[structure_id]['latest_date']:
				fee_payment_map[structure_id]['latest_mode'] = payment.payment_mode
				fee_payment_map[structure_id]['latest_date'] = payment.payment_date

		for structure in fee_structures:
			paid_total = fee_payment_map.get(structure.id, {}).get('paid_total', 0)
			pending_total = max(structure.total_fee - paid_total, 0)
			status_label = 'Cleared' if pending_total == 0 and structure.total_fee > 0 else ('Partial' if paid_total > 0 else 'Due')
			fee_payment_rows.append({
				'structure': structure,
				'paid_total': paid_total,
				'pending_total': pending_total,
				'status_label': status_label,
			})

		fee_current_structure = next((item for item in fee_structures if item.semester == profile.semester), fee_structures[-1] if fee_structures else None)
		fee_summary['annual_total'] = sum(structure.total_fee for structure in fee_structures)
		fee_summary['paid_total'] = sum(item['paid_total'] for item in fee_payment_rows)
		fee_summary['pending_balance'] = sum(item['pending_total'] for item in fee_payment_rows)
		fee_summary['paid_semesters'] = sum(1 for item in fee_payment_rows if item['pending_total'] == 0 and item['structure'].total_fee > 0)
		fee_summary['total_semesters'] = len(fee_payment_rows)
		fee_summary['clearance_percentage'] = (
			round(float((fee_summary['paid_total'] * Decimal('100')) / fee_summary['annual_total']), 1)
			if fee_summary['annual_total']
			else 0.0
		)
		if fee_current_structure is not None:
			current_paid_total = fee_payment_map.get(fee_current_structure.id, {}).get('paid_total', 0)
			current_pending = max(fee_current_structure.total_fee - current_paid_total, 0)
			fee_summary['current_semester_label'] = f"Semester {fee_current_structure.semester}"
			fee_summary['current_fee'] = fee_current_structure.total_fee
			fee_summary['payment_mode'] = fee_payment_map.get(fee_current_structure.id, {}).get('latest_mode', '-')
			fee_summary['due_date'] = fee_current_structure.due_date
			fee_summary['current_due_message'] = 'Current semester fee is fully cleared.' if current_pending == 0 else 'Current semester fee is pending.'

		fee_receipts = list(fee_payment_qs[:5])
		fee_recent_payment = fee_receipts[0] if fee_receipts else None

	return render(request, 'student_dashboard.html', {
		'profile': profile,
		'display_name': display_name,
		'avatar_text': avatar_text,
		'overall_gpa': profile.overall_gpa if profile else None,
		'selected_month': selected_month,
		'selected_month_label': selected_month_label,
		'attendance_overall_percentage': attendance_overall_percentage,
		'attendance_total_classes': attendance_total_classes,
		'attendance_present_classes': attendance_present_classes,
		'attendance_absent_classes': attendance_absent_classes,
		'monthly_overall_percentage': monthly_overall_percentage,
		'monthly_total_classes': monthly_total_classes,
		'monthly_present_classes': monthly_present_classes,
		'monthly_absent_classes': monthly_absent_classes,
		'attendance_monthly_rows': attendance_monthly_rows,
		'fee_current_structure': fee_current_structure,
		'fee_structures': fee_structures,
		'fee_payment_rows': fee_payment_rows,
		'fee_receipts': fee_receipts,
		'fee_recent_payment': fee_recent_payment,
		'fee_summary': fee_summary,
		'calendar_weekdays': calendar_weekdays,
		'calendar_cells': calendar_cells,
		'calendar_upcoming_dates': calendar_upcoming_dates,
		'calendar_month_events': calendar_month_events,
		'assignment_rows': assignment_rows,
	})


@require_POST
@login_required
def submit_assignment(request):
	profile = getattr(request.user, 'student_profile', None)
	if profile is None:
		return JsonResponse({'success': False, 'message': 'Only students can submit assignments.'}, status=403)

	assignment_id = request.POST.get('assignment_id', '').strip()
	submission_text = request.POST.get('submission_text', '').strip()

	if not assignment_id or not submission_text:
		return JsonResponse({'success': False, 'message': 'Assignment and submission text are required.'}, status=400)

	try:
		assignment_id_int = int(assignment_id)
	except ValueError:
		return JsonResponse({'success': False, 'message': 'Invalid assignment id.'}, status=400)

	assignment = StudentAssignment.objects.filter(
		id=assignment_id_int,
		is_active=True,
		course=profile.course,
		semester=profile.semester,
	).first()
	if assignment is None:
		return JsonResponse({'success': False, 'message': 'Assignment not found for your semester.'}, status=404)

	submission, _created = StudentAssignmentSubmission.objects.update_or_create(
		assignment=assignment,
		student=profile,
		defaults={
			'submission_text': submission_text,
			'status': 'Submitted',
			'marks': None,
			'feedback': '',
			'reviewed_by': None,
			'reviewed_at': None,
			'submitted_at': timezone.now(),
		},
	)

	return JsonResponse({
		'success': True,
		'message': 'Assignment submitted successfully.',
		'submission': {
			'assignment_id': assignment.id,
			'status': submission.status,
			'submitted_at': submission.submitted_at.strftime('%Y-%m-%d %H:%M'),
		},
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
