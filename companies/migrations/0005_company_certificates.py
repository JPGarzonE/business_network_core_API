# Generated by Django 3.0.5 on 2020-11-19 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0004_auto_20201117_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='certificates',
            field=models.ManyToManyField(through='companies.CompanyCertificate', to='companies.Certificate'),
        ),
    ]
