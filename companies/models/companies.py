# Models companies

# Constants
from companies.constants import VisibilityState

# Django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Django timezone
from django.utils import timezone

# Models
from companies.models import CompanyVerification
from multimedia.models import Image

# Utils
from enum import Enum


class Company(models.Model):
    """
    Company that have an account on the platform. 
    The account is of multiuser access.
    """

    id = models.BigAutoField(primary_key = True)
    
    accountname = models.CharField(
        max_length = 60, null = False, unique = True,
        help_text = _("Unique identifier name generated by the system to find the company")
    )
    
    name = models.CharField(
        help_text = _("""Real name of the company, has to be unique and is 
            the name as is going to be identified by the system."""),
        null = False, unique = True, max_length=60
    )
    
    legal_identifier = models.CharField(unique=True, max_length = 30)

    description = models.CharField(max_length=155, blank=True, null=True)

    is_buyer = models.BooleanField(
        _('buyer'), default = False,
        help_text = _('Designates if the company has a buyer profile and its capabilites')
    )

    is_supplier = models.BooleanField(
        _('supplier'), default = False,
        help_text = _('Designates if the company has a supplier profile and its capabilites')
    )

    is_verified = models.BooleanField(
        _('verified'), default = False,
        help_text = _('Set to true when the company existence and legality is verified')
    )

    visibility = models.CharField(
        max_length = 20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null = False,
        blank = False
    )

    verification = models.OneToOneField(CompanyVerification, on_delete = models.CASCADE)

    logo = models.ForeignKey(Image, models.CASCADE, blank=True, null=True)

    register_date = models.DateTimeField(
        help_text = _('date when the company was registered in the platform'), default=timezone.now
    )

    class Meta:
        db_table = 'company'


class UnregisteredCompany(models.Model):
    """
    Company that don't have an account yet but was created 
    by a registered company or a sysadmin. When the respective 
    company decide to signup, this model has to be deleted.
    """

    id = models.BigAutoField(primary_key = True)
    
    name = models.CharField(max_length=60)
    
    legal_identifier = models.CharField(unique=True, max_length = 30)

    industry = models.CharField(max_length=60)

    email = models.EmailField(unique=True)

    country = models.CharField(max_length=50)

    city = models.CharField(max_length=50)

    is_contactable = models.BooleanField(
        _('contactable'),
        default = False,
        help_text = _('Designates if the system has the permission for sending emails to the company')
    )

    class Meta:
        db_table = 'unregistered_company'