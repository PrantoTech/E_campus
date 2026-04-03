import os

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


def faculty_profile_photo_upload_to(instance, filename):
    _, extension = os.path.splitext(filename or '')
    extension = extension.lower() or '.jpg'
    faculty_id = (instance.faculty_id or f'user-{instance.user_id or "new"}').strip().upper()
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
    return f"faculty/profile_photos/faculty_{faculty_id}_{timestamp}{extension}"


class FacultyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    faculty_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    department = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=10, blank=True)
    profile_photo = models.ImageField(upload_to=faculty_profile_photo_upload_to, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.faculty_id} - {self.user.get_full_name() or self.user.username}"

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
