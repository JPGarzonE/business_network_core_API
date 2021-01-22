# Models companies

# Business Network API
from business_network_API.models import VisibilityManager, VisibilityModel

# Django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Django timezone
from django.utils import timezone

# Models
from companies.models import CompanyVerification, CompanyMember
from multimedia.models import Image

# Utils
from enum import Enum


class CompanyManager(VisibilityManager):
    """
    A custom company model manager to deal with the registration
    of a new company including user memberships logic.
    """

    def create(self, creator_user, verification = None, **company_data):
        """
        Takes the creator user of the company previously 
        created in the db and builds a relation with the 
        company through a membership.
        """
        company_data['accountname'] = self.generate_company_accountname(
            company_data['name']
        )

        if verification is None:
            verification = CompanyVerification.objects.create() # Default verification

        company = super().create(
            verification = verification, 
            **company_data
        )

        creator_membership = CompanyMember.objects.create(
            company = company, 
            user = creator_user, 
            company_accountname = company.accountname,
            company_name = company.name, 
            user_email = creator_user.email,
            user_username = creator_user.username, 
            user_full_name = creator_user.full_name
        )

        return company, creator_membership

    def generate_company_accountname(self, company_name):
        """Recieve the name of the company and generate a valid accountname for it."""
        accountname_lower = company_name.lower()
        generated_accountname = accountname_lower.strip().replace(" ", ".")
        i = 0
        while True:
            accountname = generated_accountname if i == 0 else generated_accountname + str(i)
            try:
                self.get( accountname = accountname )
            except Company.DoesNotExist:
                break
            
            i += 1
        
        return accountname


class Company(VisibilityModel):
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

    verification = models.OneToOneField(CompanyVerification, on_delete = models.CASCADE)

    logo = models.ForeignKey(Image, models.CASCADE, blank=True, null=True)

    register_date = models.DateTimeField(
        help_text = _('date when the company was registered in the platform'), default=timezone.now
    )

    objects = CompanyManager()

    def __str__(self):
        return self.accountname

    class Meta:
        db_table = 'company'

    def save(self, *args, **kwargs):
        """Manage denormalization with the CompanyMember model."""

        if self.pk:
            company_members = CompanyMember.objects.filter(
                company = self)
            
            for membership in company_members:
                membership.company_accountname = self.accountname
                membership.company_name = self.name
                membership.save()

        super(Company, self).save(*args, **kwargs)



class UnregisteredCompany(models.Model):
    """
    Company that don't have an account yet but was created 
    by a registered company or a sysadmin. When the respective 
    company decide to signup, this model has to be deleted.
    """

    id = models.BigAutoField(primary_key = True)
    
    name = models.CharField(max_length=60)
    
    legal_identifier = models.CharField(
        unique=True, max_length = 30, blank=True, null=True
    )

    industry = models.CharField(
        max_length=60, blank=True, null=True
    )

    email = models.EmailField(
        unique=True, blank=True, null=True
    )

    country = models.CharField(
        max_length=50, blank=True, null=True
    )

    city = models.CharField(
        max_length=50, blank=True, null=True
    )

    is_contactable = models.BooleanField(
        _('contactable'),
        default = False,
        help_text = _('Designates if the system has the permission for sending emails to the company')
    )

    class Meta:
        db_table = 'unregistered_company'