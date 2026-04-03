from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0008_studentprofile_overall_gpa'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='academiccalendarevent',
            name='event_type',
            field=models.CharField(choices=[('Event', 'Event'), ('Holiday', 'Holiday'), ('Exam', 'Exam'), ('Notice', 'Notice'), ('Meeting', 'Meeting')], default='Event', max_length=20),
        ),
        migrations.AddField(
            model_name='academiccalendarevent',
            name='posted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posted_academic_events', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='academiccalendarevent',
            name='visibility',
            field=models.CharField(choices=[('ALL', 'All Users'), ('FACULTY_ADMIN', 'Faculty and Admin Only')], default='ALL', max_length=20),
        ),
        migrations.CreateModel(
            name='StudentAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('course', models.CharField(choices=[('DCST', 'DCST'), ('DME', 'DME'), ('DCE', 'DCE'), ('DSE', 'DSE'), ('DCFS', 'DCFS'), ('DETC', 'DETC'), ('DEE', 'DEE')], max_length=10)),
                ('semester', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')], max_length=1)),
                ('due_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('posted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posted_student_assignments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['due_date', '-created_at'],
            },
        ),
    ]
