# Generated by Django 3.0.5 on 2020-06-23 22:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('multimedia', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='verification',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='documents', to='users.Verification'),
        ),
    ]