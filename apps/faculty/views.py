from datetime import date
import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Case, Count, IntegerField, Sum, When
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import FacultyProfile
from apps.students.models import StudentAttendance, StudentProfile


def _normalize_department(value: str) -> str:
    return re.sub(r'[^A-Z0-9]+', '', (value or '').upper())


def _courses_for_department(department: str) -> set[str]:
    normalized = _normalize_department(department)
    if not normalized:
        return set()

    explicit_map = {
        'DCST': {'DCST'},
        'DME': {'DME'},
        'DCE': {'DCE'},
        'DSE': {'DSE'},
        'DCFS': {'DCFS'},
        'DETC': {'DETC'},
        'DEE': {'DEE'},
        'CST': {'DCST'},
        'CSE': {'DCST'},
        'ECE': {'DETC'},
        'EEE': {'DEE'},
    }

    if normalized in explicit_map:
        return explicit_map[normalized]

    keyword_map = [
        ('COMPUTER', {'DCST'}),
        ('MECHANICAL', {'DME'}),
        ('CIVIL', {'DCE'}),
        ('SURVEY', {'DSE'}),
        ('FOOD', {'DCFS'}),
        ('ELECTRONICS', {'DETC'}),
        ('ELECTRICAL', {'DEE'}),
    ]

    for keyword, courses in keyword_map:
        if keyword in normalized:
            return courses
    return set()


def _can_manage_student(user, student_profile: StudentProfile) -> bool:
    if user.is_superuser or user.is_staff:
        return True

    faculty_profile = getattr(user, 'faculty_profile', None)
    if faculty_profile is None:
        return False

    allowed_courses = _courses_for_department(faculty_profile.department)
    if not allowed_courses:
        return False

    return student_profile.course in allowed_courses


def _can_assign_course(user, course_code: str) -> bool:
    if user.is_superuser or user.is_staff:
        return True

    faculty_profile = getattr(user, 'faculty_profile', None)
    if faculty_profile is None:
        return False

    return course_code in _courses_for_department(faculty_profile.department)


def _can_assign_advisor(user, advisor_profile: FacultyProfile) -> bool:
    if user.is_superuser or user.is_staff:
        return True

    faculty_profile = getattr(user, 'faculty_profile', None)
    if faculty_profile is None:
        return False

    if advisor_profile.user_id == user.id:
        return True

    return _normalize_department(advisor_profile.department) == _normalize_department(faculty_profile.department)


@require_POST
def faculty_login(request):
    email = request.POST.get('email', '').strip().lower()
    password = request.POST.get('password', '')

    if not email or not password:
        return JsonResponse({'success': False, 'message': 'Email and password are required.'}, status=400)

    if '@' not in email:
        faculty_id_candidate = email.strip().upper()
        if FacultyProfile.objects.filter(faculty_id=faculty_id_candidate).exists():
            return JsonResponse({
                'success': False,
                'message': 'Use faculty email to login. Faculty ID is only for admin record management.',
            }, status=400)

    profile = FacultyProfile.objects.select_related('user').filter(user__email=email).first()
    if profile is None:
        return JsonResponse({'success': False, 'message': 'Invalid faculty credentials.'}, status=401)

    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({'success': False, 'message': 'Invalid faculty credentials.'}, status=401)

    login(request, user)
    return JsonResponse({'success': True, 'redirect_url': '/faculty/dashboard/'})


@login_required
def faculty_dashboard(request):
    profile = getattr(request.user, 'faculty_profile', None)
    is_admin_user = request.user.is_superuser or request.user.is_staff
    if profile is None and not is_admin_user:
        return redirect('/')

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

    selected_attendance_date = today
    selected_attendance_date_value = request.GET.get('attendance_date', '').strip()
    if selected_attendance_date_value:
        try:
            selected_attendance_date = date.fromisoformat(selected_attendance_date_value)
        except ValueError:
            selected_attendance_date = today

    students_qs = StudentProfile.objects.select_related('user', 'advisor_faculty__user').order_by('course', 'semester', 'roll_no')
    scope_label = 'All Departments'
    if not is_admin_user:
        allowed_courses = _courses_for_department(profile.department)
        scope_label = profile.department or 'Unknown Department'
        students_qs = students_qs.filter(course__in=allowed_courses) if allowed_courses else StudentProfile.objects.none()

    students = list(students_qs)
    attendance_base_qs = StudentAttendance.objects.filter(student__in=students)
    overall_total_entries = attendance_base_qs.count()
    overall_present_entries = attendance_base_qs.filter(is_present=True).count()
    overall_attendance_percentage = round((overall_present_entries * 100.0 / overall_total_entries), 1) if overall_total_entries else 0.0

    monthly_attendance_qs = attendance_base_qs.filter(attendance_date__year=selected_year, attendance_date__month=selected_month_number)
    monthly_total_entries = monthly_attendance_qs.count()
    monthly_present_entries = monthly_attendance_qs.filter(is_present=True).count()
    monthly_absent_entries = max(monthly_total_entries - monthly_present_entries, 0)
    monthly_average_percentage = round((monthly_present_entries * 100.0 / monthly_total_entries), 1) if monthly_total_entries else 0.0
    monthly_students_marked = monthly_attendance_qs.values('student_id').distinct().count()

    monthly_report = monthly_attendance_qs.values('student_id').annotate(
        total=Count('id'),
        present=Sum(Case(When(is_present=True, then=1), default=0, output_field=IntegerField())),
    )
    monthly_report_map = {item['student_id']: item for item in monthly_report}

    overall_report = attendance_base_qs.values('student_id').annotate(
        total=Count('id'),
        present=Sum(Case(When(is_present=True, then=1), default=0, output_field=IntegerField())),
    )
    overall_report_map = {item['student_id']: item for item in overall_report}

    selected_day_records = attendance_base_qs.filter(attendance_date=selected_attendance_date).values('student_id', 'is_present')
    selected_day_status_map = {
        entry['student_id']: ('Present' if entry['is_present'] else 'Absent')
        for entry in selected_day_records
    }

    attendance_rows = []
    for student in students:
        month_item = monthly_report_map.get(student.id)
        month_total = month_item['total'] if month_item else 0
        month_present = month_item['present'] if month_item and month_item['present'] is not None else 0
        month_absent = max(month_total - month_present, 0)
        month_percentage = round((month_present * 100.0 / month_total), 1) if month_total else 0.0

        overall_item = overall_report_map.get(student.id)
        overall_total = overall_item['total'] if overall_item else 0
        overall_present = overall_item['present'] if overall_item and overall_item['present'] is not None else 0
        overall_percentage = round((overall_present * 100.0 / overall_total), 1) if overall_total else 0.0

        attendance_rows.append({
            'student': student,
            'month_total': month_total,
            'month_present': month_present,
            'month_absent': month_absent,
            'month_percentage': month_percentage,
            'overall_percentage': overall_percentage,
            'selected_day_status': selected_day_status_map.get(student.id, ''),
        })

    display_name = request.user.get_full_name().strip() or (profile.faculty_id if profile else request.user.username)
    avatar_text = ''.join(part[0].upper() for part in display_name.split()[:2]) or display_name[:2].upper()
    faculty_profiles = FacultyProfile.objects.select_related('user').order_by('faculty_id') if is_admin_user else FacultyProfile.objects.none()
    if is_admin_user:
        advisor_faculty_options = FacultyProfile.objects.select_related('user').order_by('faculty_id')
    else:
        normalized_dept = _normalize_department(profile.department if profile else '')
        advisor_faculty_options = FacultyProfile.objects.select_related('user').order_by('faculty_id')
        if normalized_dept:
            advisor_faculty_options = [
                item for item in advisor_faculty_options
                if _normalize_department(item.department) == normalized_dept
            ]
        else:
            advisor_faculty_options = [profile] if profile else []

    return render(request, 'faculty_dashboard.html', {
        'profile': profile,
        'display_name': display_name,
        'avatar_text': avatar_text,
        'students': students_qs,
        'students_count': students_qs.count(),
        'scope_label': scope_label,
        'is_admin_user': is_admin_user,
        'overall_attendance_percentage': overall_attendance_percentage,
        'selected_month': selected_month,
        'selected_month_label': selected_month_label,
        'selected_attendance_date': selected_attendance_date.isoformat(),
        'monthly_total_entries': monthly_total_entries,
        'monthly_present_entries': monthly_present_entries,
        'monthly_absent_entries': monthly_absent_entries,
        'monthly_average_percentage': monthly_average_percentage,
        'monthly_students_marked': monthly_students_marked,
        'attendance_rows': attendance_rows,
        'faculty_profiles': faculty_profiles,
        'advisor_faculty_options': advisor_faculty_options,
        'course_choices': StudentProfile.COURSE_CHOICES,
        'semester_choices': StudentProfile.SEMESTER_CHOICES,
        'gender_choices': StudentProfile.GENDER_CHOICES,
    })


@require_POST
@login_required
def mark_student_attendance(request):
    student_id = request.POST.get('student_id', '').strip().upper()
    attendance_date_value = request.POST.get('attendance_date', '').strip()
    status = request.POST.get('status', '').strip().lower()

    if not student_id:
        return JsonResponse({'success': False, 'message': 'Student ID is required.'}, status=400)

    if not attendance_date_value:
        return JsonResponse({'success': False, 'message': 'Attendance date is required.'}, status=400)

    try:
        attendance_date = date.fromisoformat(attendance_date_value)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Attendance date must be valid.'}, status=400)

    if status not in {'present', 'absent'}:
        return JsonResponse({'success': False, 'message': 'Attendance status must be Present or Absent.'}, status=400)

    student = StudentProfile.objects.select_related('user').filter(student_id=student_id).first()
    if student is None:
        return JsonResponse({'success': False, 'message': 'Student not found.'}, status=404)

    if not _can_manage_student(request.user, student):
        return JsonResponse({'success': False, 'message': 'You do not have permission to mark this student.'}, status=403)

    is_present = status == 'present'
    StudentAttendance.objects.update_or_create(
        student=student,
        attendance_date=attendance_date,
        defaults={'is_present': is_present},
    )

    total_entries = StudentAttendance.objects.filter(student=student).count()
    present_entries = StudentAttendance.objects.filter(student=student, is_present=True).count()
    average_percentage = round((present_entries * 100.0 / total_entries), 1) if total_entries else 0.0

    return JsonResponse({
        'success': True,
        'message': 'Attendance saved successfully.',
        'student_id': student.student_id,
        'status': 'Present' if is_present else 'Absent',
        'average_attendance': average_percentage,
    })


@require_POST
@login_required
@transaction.atomic
def update_student_details(request):
    student_id = request.POST.get('student_id', '').strip().upper()
    if not student_id:
        return JsonResponse({'success': False, 'message': 'Student ID is required.'}, status=400)

    student = StudentProfile.objects.select_related('user').filter(student_id=student_id).first()
    if student is None:
        return JsonResponse({'success': False, 'message': 'Student not found.'}, status=404)

    if not _can_manage_student(request.user, student):
        return JsonResponse({'success': False, 'message': 'You do not have permission to edit this student.'}, status=403)

    full_name = request.POST.get('full_name', '').strip()
    email = request.POST.get('email', '').strip().lower()
    mobile = request.POST.get('mobile', '').strip()
    semester = request.POST.get('semester', '').strip()
    course = request.POST.get('course', '').strip()
    gender = request.POST.get('gender', '').strip()
    roll_no = request.POST.get('roll_no', '').strip()
    dob = request.POST.get('date_of_birth', '').strip()
    guardian_name = request.POST.get('guardian_name', '').strip()
    guardian_contact = request.POST.get('guardian_contact', '').strip()
    advisor_faculty_id = request.POST.get('advisor_faculty_id', '').strip().upper()
    overall_gpa_value = request.POST.get('overall_gpa', '').strip()
    address = request.POST.get('address')
    if address is not None:
        address = address.strip()

    if not all([full_name, email, mobile, semester, course, gender, roll_no, dob, guardian_name]):
        return JsonResponse({'success': False, 'message': 'Please fill all required student fields.'}, status=400)

    if semester not in {choice for choice, _ in StudentProfile.SEMESTER_CHOICES}:
        return JsonResponse({'success': False, 'message': 'Invalid semester value.'}, status=400)

    if course not in {choice for choice, _ in StudentProfile.COURSE_CHOICES}:
        return JsonResponse({'success': False, 'message': 'Invalid course value.'}, status=400)

    if not _can_assign_course(request.user, course):
        return JsonResponse({'success': False, 'message': 'You cannot assign this course.'}, status=403)

    if gender not in {choice for choice, _ in StudentProfile.GENDER_CHOICES}:
        return JsonResponse({'success': False, 'message': 'Invalid gender value.'}, status=400)

    if not mobile.isdigit() or len(mobile) != 10:
        return JsonResponse({'success': False, 'message': 'Mobile number must be 10 digits.'}, status=400)

    if not roll_no.isdigit():
        return JsonResponse({'success': False, 'message': 'Roll number must be numeric.'}, status=400)

    try:
        dob_date = date.fromisoformat(dob)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Date of birth must be valid.'}, status=400)

    if guardian_contact and (not guardian_contact.isdigit() or len(guardian_contact) != 10):
        return JsonResponse({'success': False, 'message': 'Guardian contact must be 10 digits.'}, status=400)

    overall_gpa = None
    if overall_gpa_value:
        try:
            overall_gpa = round(float(overall_gpa_value), 2)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Overall GPA must be a valid number.'}, status=400)
        if overall_gpa < 0 or overall_gpa > 10:
            return JsonResponse({'success': False, 'message': 'Overall GPA must be between 0 and 10.'}, status=400)

    advisor_profile = None
    if advisor_faculty_id:
        advisor_profile = FacultyProfile.objects.filter(faculty_id=advisor_faculty_id).first()
        if advisor_profile is None:
            return JsonResponse({'success': False, 'message': 'Advisor faculty not found.'}, status=404)
        if not _can_assign_advisor(request.user, advisor_profile):
            return JsonResponse({'success': False, 'message': 'You do not have permission to assign this advisor.'}, status=403)

    existing_email_user = student.user.__class__.objects.filter(email=email).exclude(pk=student.user_id).first()
    if existing_email_user is not None:
        return JsonResponse({'success': False, 'message': 'Email is already used by another account.'}, status=400)

    roll_no_int = int(roll_no)
    if StudentProfile.objects.exclude(pk=student.pk).filter(roll_no=roll_no_int).exists():
        return JsonResponse({'success': False, 'message': 'Roll number is already assigned to another student.'}, status=400)

    student.user.first_name = full_name
    student.user.email = email
    student.user.username = email
    student.user.save(update_fields=['first_name', 'email', 'username'])

    student.roll_no = roll_no_int
    student.course = course
    student.gender = gender
    student.date_of_birth = dob_date
    student.mobile = mobile
    student.semester = semester
    student.guardian_name = guardian_name
    student.guardian_contact = guardian_contact
    student.advisor_faculty = advisor_profile
    student.overall_gpa = overall_gpa
    update_fields = [
        'roll_no',
        'course',
        'gender',
        'date_of_birth',
        'mobile',
        'semester',
        'guardian_name',
        'guardian_contact',
        'advisor_faculty',
        'overall_gpa',
    ]
    if address is not None:
        student.address = address
        update_fields.append('address')

    student.save(update_fields=update_fields)

    return JsonResponse({'success': True, 'message': 'Student details updated successfully.'})


@require_POST
@login_required
@transaction.atomic
def update_faculty_details(request):
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'success': False, 'message': 'Only admin can update faculty details.'}, status=403)

    faculty_id = request.POST.get('faculty_id', '').strip().upper()
    if not faculty_id:
        return JsonResponse({'success': False, 'message': 'Faculty ID is required.'}, status=400)

    profile = FacultyProfile.objects.select_related('user').filter(faculty_id=faculty_id).first()
    if profile is None:
        return JsonResponse({'success': False, 'message': 'Faculty profile not found.'}, status=404)

    full_name = request.POST.get('full_name', '').strip()
    email = request.POST.get('email', '').strip().lower()
    department = request.POST.get('department', '').strip()
    mobile = request.POST.get('mobile', '').strip()

    if not full_name or not email:
        return JsonResponse({'success': False, 'message': 'Faculty name and email are required.'}, status=400)

    if mobile and (not mobile.isdigit() or len(mobile) != 10):
        return JsonResponse({'success': False, 'message': 'Faculty mobile must be 10 digits.'}, status=400)

    duplicate_user = User.objects.filter(email=email).exclude(pk=profile.user_id).first()
    if duplicate_user is not None:
        return JsonResponse({'success': False, 'message': 'Email is already used by another account.'}, status=400)

    profile.user.first_name = full_name
    profile.user.email = email
    profile.user.username = email
    profile.user.save(update_fields=['first_name', 'email', 'username'])

    profile.department = department
    profile.mobile = mobile
    profile.save(update_fields=['department', 'mobile'])

    return JsonResponse({'success': True, 'message': 'Faculty details updated successfully.'})


@require_POST
@login_required
def upload_profile_photo(request):
    profile = getattr(request.user, 'faculty_profile', None)
    if profile is None:
        return redirect('/faculty/dashboard/#profile')

    photo = request.FILES.get('profile_photo')
    if photo is None:
        return redirect('/faculty/dashboard/#profile')

    content_type = getattr(photo, 'content_type', '') or ''
    if not content_type.startswith('image/'):
        return redirect('/faculty/dashboard/#profile')

    max_size_bytes = 5 * 1024 * 1024
    if photo.size > max_size_bytes:
        return redirect('/faculty/dashboard/#profile')

    profile.profile_photo = photo
    profile.save(update_fields=['profile_photo'])
    return redirect('/faculty/dashboard/#profile')


@require_POST
def faculty_forgot_password(request):
    faculty_id = request.POST.get('faculty_id', '').strip().upper()
    dob = request.POST.get('dob', '').strip()
    new_password = request.POST.get('new_password', '')
    confirm_password = request.POST.get('confirm_password', '')

    if not faculty_id or not dob or not new_password or not confirm_password:
        return JsonResponse({'success': False, 'message': 'Please fill all required fields.'}, status=400)

    if new_password != confirm_password:
        return JsonResponse({'success': False, 'message': 'Passwords do not match.'}, status=400)

    if len(new_password) < 8:
        return JsonResponse({'success': False, 'message': 'Password must be at least 8 characters.'}, status=400)

    try:
        dob_date = date.fromisoformat(dob)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Enter a valid date of birth.'}, status=400)

    profile = FacultyProfile.objects.select_related('user').filter(faculty_id=faculty_id, date_of_birth=dob_date).first()
    if profile is None:
        return JsonResponse({'success': False, 'message': 'Faculty ID and DOB did not match.'}, status=404)

    user = profile.user
    user.set_password(new_password)
    user.save(update_fields=['password'])

    return JsonResponse({
        'success': True,
        'message': 'Password reset successful. Please login with your new password.',
        'login_id': profile.user.email,
    })


@require_POST
@login_required
def faculty_logout(request):
    logout(request)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'redirect_url': '/'})
    return redirect('/')
