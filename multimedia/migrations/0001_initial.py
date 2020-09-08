# Generated by Django 3.0.5 on 2020-06-24 20:23

from django.db import migrations, models
import django.utils.timezone
import multimedia.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Is the name as the document is saved in the storage system', max_length=60)),
                ('relative_path', models.TextField(blank=True, help_text='path inside the storage (s3 bucket) - Not take in account domain (Ej: https://...)')),
                ('absolute_path', models.TextField(blank=True, help_text='the complete path where is in the internet')),
                ('purpose', models.CharField(help_text='Describes the need that the document meets', max_length=35)),
                ('type', models.CharField(blank=True, choices=[(multimedia.models.Document.Types['PDF'], (('PDF', 'application/pdf'),))], help_text='Format, Ej: pdf, png, etc...', max_length=17)),
                ('valid', models.BooleanField(default=None, help_text='Store if the document is in the correct format', null=True)),
                ('uploaded', models.BooleanField(default=False, help_text='stores if the file could be uploaded')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date when was created')),
            ],
            options={
                'db_table': 'document',
            },
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, help_text='the name of the file as is located', max_length=120)),
                ('relative_path', models.TextField(blank=True, help_text='path inside the storage (s3 bucket) - Not take in account domain (Ej: https://...)')),
                ('absolute_path', models.TextField(blank=True, help_text='the complete path where is in the internet')),
                ('width', models.CharField(max_length=8)),
                ('height', models.CharField(max_length=8)),
                ('size', models.CharField(max_length=8)),
                ('type', models.CharField(choices=[(multimedia.models.Image.Types['JPEG'], (('JPEG', 'image/JPEG'),)), (multimedia.models.Image.Types['JPG'], (('JPG', 'image/JPG'),)), (multimedia.models.Image.Types['PNG'], (('PNG', 'image/PNG'),))], max_length=17)),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date when was created')),
                ('uploaded', models.BooleanField(default=False, help_text='stores if the file could be uploaded')),
            ],
            options={
                'db_table': 'media',
            },
        ),
    ]
