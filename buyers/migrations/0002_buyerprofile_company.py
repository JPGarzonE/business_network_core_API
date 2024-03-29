# Generated by Django 3.0.5 on 2021-02-18 01:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('buyers', '0001_initial'),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='buyerprofile',
            name='company',
            field=models.OneToOneField(help_text='Company owner of the buyer profile.', on_delete=django.db.models.deletion.PROTECT, to='companies.Company'),
        ),
    ]
