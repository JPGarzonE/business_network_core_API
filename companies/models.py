# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from users.models import VisibilityState

# Utils
from enum import Enum

class Company(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField('users.User', on_delete = models.PROTECT)
    nit = models.CharField(unique=True, max_length = 20)
    name = models.CharField(max_length=60)
    industry = models.CharField(max_length=60, blank=True, null=True)
    verification = models.ForeignKey('users.Verification', models.PROTECT)
    web_url = models.CharField(max_length=150, blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    
    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'company'


class Companysocialnetwork(models.Model):
    company = models.OneToOneField(Company, models.PROTECT, primary_key=True)
    social_network = models.ForeignKey('Socialnetwork', models.PROTECT)

    class Meta:
        db_table = 'companysocialnetwork'
        unique_together = (('company', 'social_network'),)


class Contact(models.Model):
    id = models.BigAutoField(primary_key=True)
    phone = models.CharField(max_length = 15,blank=True, null=True)
    ext_phone = models.CharField(max_length=5, blank=True, null=True)
    company = models.ForeignKey(Company, models.PROTECT)
    email = models.CharField(max_length=60, blank=True, null=True)
    principal = principal = models.BooleanField(default = False)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'contact'

class Dnaelement(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=45)
    category = models.CharField(max_length=45)
    media = models.ForeignKey('Media', models.PROTECT, blank=True, null=True)
    company = models.ForeignKey(Company, models.PROTECT)
    description = models.CharField(max_length=155, blank=True, null=True)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'dnaelement'


class Employee(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    hired = models.CharField(max_length=1)
    celphone = models.CharField(unique=True, max_length=14)
    charge = models.CharField(max_length=45)
    company = models.ForeignKey(Company, models.PROTECT)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'employee'


class Employeesocialnetwork(models.Model):
    employee = models.OneToOneField(Employee, models.PROTECT, primary_key=True)
    social_network = models.ForeignKey('Socialnetwork', models.PROTECT)

    class Meta:
        db_table = 'employeesocialnetwork'
        unique_together = (('employee', 'social_network'),)


class Importantevents(models.Model):
    id = models.BigAutoField(primary_key=True)
    source_url = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=155, blank=True, null=True)
    media = models.ForeignKey('Media', models.PROTECT, blank=True, null=True)
    company = models.ForeignKey(Company, models.PROTECT, db_column='Company_id')  # Field name made lowercase.

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'importantevents'


class Interest(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=60)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=50, blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    company = models.ForeignKey(Company, models.PROTECT)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'interest'


class Location(models.Model):
    id = models.BigAutoField(primary_key=True)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=45, blank=True, null=True)
    address = models.CharField(max_length=45, blank=True, null=True)
    zip = models.CharField(max_length=45, blank=True, null=True)
    principal = models.BooleanField(default = False)
    company = models.ForeignKey(Company, models.PROTECT)
    media = models.ForeignKey('Media', models.PROTECT, blank=True, null=True)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'location'


class Media(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=60)

    class Types(Enum):
        IMAGE = 'Image'
        VIDEO = 'Video'

    type = models.CharField(
        max_length=5,
        choices = [(typeOption, typeOption.value) for typeOption in Types],
        null=False,
        blank=False,    
    )

    class Meta:
        db_table = 'media'


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    price = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(max_length=60)
    description = models.CharField(max_length=155, blank=True, null=True)
    company = models.ForeignKey(Company, models.PROTECT)
    media = models.ForeignKey(Media, models.PROTECT, blank=True, null=True)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'product'


class Service(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    price = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(max_length=60)
    description = models.CharField(max_length=155, blank=True, null=True)
    company = models.ForeignKey(Company, models.PROTECT)
    media = models.ForeignKey(Media, models.PROTECT, blank=True, null=True)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'service'


class Socialnetwork(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=45, blank=True, null=True)
    username = models.CharField(max_length=45, blank=True, null=True)
    url = models.CharField(max_length=150, blank=True, null=True)
    privacy = models.CharField(max_length=9, blank=True, null=True)
    profile_image_url = models.CharField(max_length=150, blank=True, null=True)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'socialnetwork'
