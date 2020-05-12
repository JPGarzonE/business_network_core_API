# Generated by Django 3.0.5 on 2020-05-12 21:24

import companies.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_auto_20200430_0827'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='media',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='companies.Media'),
        ),
        migrations.AlterField(
            model_name='media',
            name='type',
            field=models.CharField(choices=[(companies.models.Media.Types['IMAGE'], 'Image'), (companies.models.Media.Types['VIDEO'], 'Video')], max_length=5),
        ),
    ]