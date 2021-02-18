# Generated by Django 3.0.5 on 2021-02-18 01:16

import companies.models.verifications
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('multimedia', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('state', models.CharField(choices=[('PRIV', 'Private'), ('OPEN', 'Open'), ('DEL', 'Deleted')], default='OPEN', max_length=4)),
                ('changed_at', models.DateTimeField(auto_now=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('accountname', models.CharField(help_text='Unique identifier name generated by the system to find the company', max_length=60, unique=True)),
                ('name', models.CharField(help_text='Real name of the company, has to be unique and is \n            the name as is going to be identified by the system.', max_length=60, unique=True)),
                ('legal_identifier', models.CharField(max_length=30, unique=True)),
                ('description', models.CharField(blank=True, max_length=155, null=True)),
                ('is_buyer', models.BooleanField(default=False, help_text='Designates if the company has a buyer profile and its capabilites', verbose_name='buyer')),
                ('is_supplier', models.BooleanField(default=False, help_text='Designates if the company has a supplier profile and its capabilites', verbose_name='supplier')),
                ('is_verified', models.BooleanField(default=False, help_text='Set to true when the company existence and legality is verified', verbose_name='verified')),
                ('register_date', models.DateTimeField(default=django.utils.timezone.now, help_text='date when the company was registered in the platform')),
            ],
            options={
                'db_table': 'company',
            },
        ),
        migrations.CreateModel(
            name='CompanyVerification',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('verified', models.BooleanField(default=False, help_text='Set to true when the verification process has ended succesfully')),
                ('state', models.CharField(choices=[(companies.models.verifications.CompanyVerification.States['NONE'], 'None'), (companies.models.verifications.CompanyVerification.States['INPROGRESS'], 'InProgress'), (companies.models.verifications.CompanyVerification.States['STOPPED'], 'Stopped'), (companies.models.verifications.CompanyVerification.States['LOCKED'], 'Locked'), (companies.models.verifications.CompanyVerification.States['SUCCESS'], 'Success')], default='None', max_length=15)),
                ('application_date', models.DateTimeField(default=django.utils.timezone.now, help_text='date when was the verification process was started')),
                ('finish_date', models.DateTimeField(blank=True, help_text='date when was the verification process was closed', null=True)),
            ],
            options={
                'db_table': 'company_verification',
            },
        ),
        migrations.CreateModel(
            name='UnregisteredCompany',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=60)),
                ('legal_identifier', models.CharField(blank=True, max_length=30, null=True, unique=True)),
                ('industry', models.CharField(blank=True, max_length=60, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('is_contactable', models.BooleanField(default=False, help_text='Designates if the system has the permission for sending emails to the company', verbose_name='contactable')),
            ],
            options={
                'db_table': 'unregistered_company',
            },
        ),
        migrations.CreateModel(
            name='UnregisteredRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(blank=True, help_text='Type of relationship between a registered and a non registered company.', max_length=30, null=True)),
                ('requester', models.ForeignKey(help_text='Is the company that request the relationship.It exist in the platform and is registered', on_delete=django.db.models.deletion.PROTECT, related_name='unregistered_relationship_requester', to='companies.Company')),
                ('unregistered', models.ForeignKey(help_text='Is the company that is not official registered in the platform.It was created by another user that could not find its partners registeredbut wants to show it in its relationships, or was created by a sysadmin', on_delete=django.db.models.deletion.PROTECT, related_name='relationship_unregistered', to='companies.UnregisteredCompany')),
            ],
            options={
                'db_table': 'unregistered_relationship',
            },
        ),
        migrations.CreateModel(
            name='RelationshipRequest',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('message', models.TextField(blank=True, help_text='Message that the company requester include in the relationship request', null=True, verbose_name='Message')),
                ('blocked', models.BooleanField(default=False, help_text="Indicates if the relationship wasn't accepted by the addressed company", verbose_name='blocked')),
                ('created_date', models.DateTimeField(auto_now_add=True, help_text='date when the request was sent by the requester company')),
                ('last_updated', models.DateTimeField(auto_now=True, help_text='date when the request was last updated by some of the members.')),
                ('addressed', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='relationship_request_addressed', to='companies.Company')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='relationship_request_requester', to='companies.Company')),
            ],
            options={
                'db_table': 'relationship_request',
            },
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(blank=True, help_text='Type of relationship that has been built between the companies', max_length=30, null=True)),
                ('addressed', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='relationship_addressed', to='companies.Company')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='relationship_requester', to='companies.Company')),
            ],
            options={
                'db_table': 'relationship',
            },
        ),
        migrations.CreateModel(
            name='CompanyVerificationFile',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('company_verification', models.ForeignKey(help_text='Verification process that has been opened for verify a company.', on_delete=django.db.models.deletion.PROTECT, to='companies.CompanyVerification')),
                ('file', models.ForeignKey(help_text='File that is part of the company verification process', on_delete=django.db.models.deletion.CASCADE, to='multimedia.File')),
            ],
            options={
                'db_table': 'company_verification_file',
            },
        ),
        migrations.AddField(
            model_name='companyverification',
            name='files',
            field=models.ManyToManyField(through='companies.CompanyVerificationFile', to='multimedia.File', verbose_name='files'),
        ),
        migrations.CreateModel(
            name='CompanyMember',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('number_of_logins_in_supplier_profile', models.PositiveIntegerField(default=0)),
                ('number_of_logins_in_buyer_profile', models.PositiveIntegerField(default=0)),
                ('company_accountname', models.CharField(help_text='Attribute accountname of the company model. Denormalized for fast access.', max_length=60, unique=True)),
                ('company_name', models.CharField(help_text='Attribute name of the company model. Denormalized for fast access.', max_length=60, unique=True)),
                ('user_email', models.EmailField(help_text='Attribute email of the user model. Denormalized for fast access.', max_length=254, unique=True)),
                ('user_username', models.CharField(help_text='Attribute username of the user model. Denormalized for fast access.', max_length=60, unique=True)),
                ('user_full_name', models.CharField(help_text='Attribute full_name of the user model. Denormalized for fast access.', max_length=50)),
                ('company', models.ForeignKey(help_text='Company that is accesible for its members (user).', on_delete=django.db.models.deletion.PROTECT, to='companies.Company', verbose_name='company account')),
            ],
            options={
                'db_table': 'company_member',
            },
        ),
    ]
