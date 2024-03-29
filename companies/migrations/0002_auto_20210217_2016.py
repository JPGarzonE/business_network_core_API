# Generated by Django 3.0.5 on 2021-02-18 01:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('multimedia', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='companymember',
            name='user',
            field=models.ForeignKey(help_text='User that has access to the company account', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='company employee'),
        ),
        migrations.AddField(
            model_name='company',
            name='logo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='multimedia.Image'),
        ),
        migrations.AddField(
            model_name='company',
            name='verification',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='companies.CompanyVerification'),
        ),
        migrations.AlterUniqueTogether(
            name='unregisteredrelationship',
            unique_together={('requester', 'unregistered')},
        ),
        migrations.AlterUniqueTogether(
            name='relationship',
            unique_together={('requester', 'addressed')},
        ),
        migrations.AlterUniqueTogether(
            name='companymember',
            unique_together={('company', 'user')},
        ),
    ]
