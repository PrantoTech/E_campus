from django import forms
from django.contrib import admin
from django.contrib.auth.models import User

from .models import FacultyProfile


class FacultyProfileCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=150, required=False)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True)

    class Meta:
        model = FacultyProfile
        fields = ('faculty_id', 'date_of_birth', 'department', 'mobile', 'profile_photo')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    def save(self, commit=True):
        email = self.cleaned_data['email'].strip().lower()
        full_name = self.cleaned_data.get('full_name', '').strip()
        password = self.cleaned_data['password']

        first_name = ''
        last_name = ''
        if full_name:
            parts = full_name.split()
            first_name = parts[0]
            last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        profile = super().save(commit=False)
        profile.user = user
        if commit:
            profile.save()
        return profile


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'user', 'department', 'mobile', 'created_at')
    search_fields = ('faculty_id', 'user__username', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Faculty Details', {
            'fields': ('user', 'faculty_id', 'date_of_birth', 'department', 'mobile', 'profile_photo', 'created_at'),
        }),
    )

    add_fieldsets = (
        ('Login Credentials', {
            'fields': ('email', 'full_name', 'password'),
        }),
        ('Faculty Details', {
            'fields': ('faculty_id', 'date_of_birth', 'department', 'mobile', 'profile_photo'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = FacultyProfileCreationForm if obj is None else forms.modelform_factory(
            FacultyProfile,
            fields=('user', 'faculty_id', 'date_of_birth', 'department', 'mobile', 'profile_photo'),
        )
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        return self.fieldsets

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.user and obj.user.email:
            normalized_email = obj.user.email.strip().lower()
            if obj.user.username != normalized_email:
                obj.user.username = normalized_email
                obj.user.save(update_fields=['username'])
