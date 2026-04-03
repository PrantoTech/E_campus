from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0009_academiccalendarevent_visibility_and_studentassignment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentAssignmentSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_text', models.TextField()),
                ('status', models.CharField(choices=[('Submitted', 'Submitted'), ('Reviewed', 'Reviewed')], default='Submitted', max_length=20)),
                ('marks', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('feedback', models.TextField(blank=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='students.studentassignment')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_assignment_submissions', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment_submissions', to='students.studentprofile')),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='studentassignmentsubmission',
            constraint=models.UniqueConstraint(fields=('assignment', 'student'), name='unique_assignment_submission_per_student'),
        ),
    ]
