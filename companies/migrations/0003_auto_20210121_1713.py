# Generated by Django 3.0.5 on 2021-01-21 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0001_initial'),
        ('companies', '0002_auto_20210117_0757'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyverification',
            name='files',
            field=models.ManyToManyField(through='companies.CompanyVerificationFile', to='multimedia.File', verbose_name='files'),
        ),
        migrations.AlterField(
            model_name='unregisteredcompany',
            name='city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='unregisteredcompany',
            name='country',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='unregisteredcompany',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='unregisteredcompany',
            name='industry',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='unregisteredcompany',
            name='legal_identifier',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
    ]
