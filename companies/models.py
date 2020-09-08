# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import User, Verification, VisibilityState
from multimedia.models import Image

# Utils
from enum import Enum

class Certificate(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=155, blank=True, null=True)
    logo = models.ForeignKey(Image, models.CASCADE, 
        help_text = "Logo that represents the certificate authority", blank=True, null=True)

    class Meta:
        db_table = 'certification'


class Company(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete = models.PROTECT)
    nit = models.CharField(unique=True, max_length = 20)
    name = models.CharField(max_length=60)
    role = models.CharField(max_length=50, blank=True, null=True)
    priority = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ForeignKey(Image, models.CASCADE, blank=True, null=True)
    industry = models.CharField(max_length=60)
    web_url = models.CharField(max_length=150, blank=True, null=True)
    description = models.CharField(max_length=155, blank=True, null=True)
    
    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'company'


class CompanyCertificate(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    certificate = models.ForeignKey(Certificate, on_delete=models.PROTECT)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'companycertificate'
        unique_together = (('company', 'certificate'),)


class CompanySocialnetwork(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    social_network = models.ForeignKey('Socialnetwork', models.CASCADE)

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
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'contact'

class Dnaelement(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=45)
    category = models.CharField(max_length=45)
    image = models.ForeignKey(Image, models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(Company, models.PROTECT)
    description = models.CharField(max_length=155, blank=True, null=True)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
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
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'employee'


class EmployeeSocialnetwork(models.Model):
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    social_network = models.ForeignKey('Socialnetwork', models.CASCADE)

    class Meta:
        db_table = 'employeesocialnetwork'
        unique_together = (('employee', 'social_network'),)


class ImportantEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    source_url = models.CharField(max_length=150, blank=True, null=True)
    name = models.CharField(max_length=45)
    description = models.CharField(max_length=155, blank=True, null=True)
    image = models.ForeignKey(Image, models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(Company, models.PROTECT, db_column='Company_id')  # Field name made lowercase.

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
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
        default = VisibilityState.OPEN.value,
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
    headquarters_image = models.ForeignKey(Image, models.CASCADE, blank=True, null=True)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'location'


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    company = models.ForeignKey(Company, models.PROTECT)
    category = models.CharField(max_length=60)
    minimum_price = models.CharField(max_length=20, blank=True, null=True)
    maximum_price = models.CharField(max_length=20, blank=True, null=True)
    tariff_heading = models.CharField(max_length = 20, blank = True, null = True)
    minimum_purchase = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=155, blank=True, null=True)

    certificates = models.ManyToManyField(Certificate, through = "ProductCertificate")
    images = models.ManyToManyField(Image, through = "ProductImage")

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'product'


class ProductCertificate(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    certificate = models.ForeignKey(Certificate, on_delete=models.PROTECT)

    class Meta:
        db_table = 'productcertificate'
        unique_together = (('product', 'certificate'),)


class ProductImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    image = models.ForeignKey(Image, models.PROTECT, unique = False)

    class Meta:
        db_table = 'productimage'
        unique_together = (('product', 'image'),)


class Service(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    price = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(max_length=60)
    description = models.CharField(max_length=155, blank=True, null=True)
    company = models.ForeignKey(Company, models.PROTECT)
    images = models.ManyToManyField(Image)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'service'


class Socialnetwork(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    username = models.CharField(max_length=45, blank=True, null=True)
    profile_url = models.CharField(max_length=150, blank=True, null=True)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'socialnetwork'


class UnregisteredCompany(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=60)
    nit = models.CharField(unique=True, max_length = 20, blank=True, null=True)
    industry = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'unregisteredcompany'


class UnregisteredRelationship(models.Model):
    requester = models.ForeignKey(
        Company, 
        models.PROTECT, 
        related_name = 'relation_requester',
        help_text = _(
            'Is the company that request the relationship.'
            'It exist in the platform and is registered'
        )
    )
    unregistered = models.ForeignKey(
        UnregisteredCompany, 
        models.PROTECT, 
        related_name = 'relation_unregistered',
        help_text = _(
            'Is the company that is not official registered in the platform.'
            'It was created by another user that could not find its partners registered'
            'but wants to show it in its relationships, or was created by an admin'
        )
    )

    type = models.CharField(max_length=30)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'unregisteredrelationship'
        unique_together = (('requester','unregistered'),)