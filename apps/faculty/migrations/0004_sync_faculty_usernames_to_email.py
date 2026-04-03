from django.db import migrations


def sync_faculty_usernames_to_email(apps, schema_editor):
    FacultyProfile = apps.get_model('faculty', 'FacultyProfile')
    for profile in FacultyProfile.objects.select_related('user').all():
        user = profile.user
        if not user:
            continue

        normalized_email = (user.email or '').strip().lower()
        if not normalized_email:
            continue

        if user.username != normalized_email:
            user.username = normalized_email
            user.save(update_fields=['username'])


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0003_alter_facultyprofile_profile_photo'),
    ]

    operations = [
        migrations.RunPython(sync_faculty_usernames_to_email, migrations.RunPython.noop),
    ]
