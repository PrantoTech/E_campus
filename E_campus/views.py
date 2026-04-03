from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST

from apps.students.models import AcademicCalendarEvent

def home(request):
    public_announcements = AcademicCalendarEvent.objects.filter(
        is_active=True,
        visibility='ALL',
    ).exclude(
        event_type='Meeting',
    ).order_by('-event_date', '-created_at')[:6]
    return render(request, 'index.html', {'public_announcements': public_announcements})

def image_gallery(request):
    return render(request, 'image_gallery.html')


def admin_logout_redirect(request):
    logout(request)
    return redirect('/')


@require_POST
def admin_login(request):
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    if not username or not password:
        return JsonResponse({'success': False, 'message': 'Username and password are required.'}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'success': False, 'message': 'Invalid admin credentials.'}, status=401)

    if not user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Use a superuser account for admin access.'}, status=403)

    login(request, user)
    return JsonResponse({'success': True, 'redirect_url': '/admin/'})