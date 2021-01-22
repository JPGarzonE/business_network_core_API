# Models buyers

# Business Network API
from business_network_API.models import VisibilityManager, VisibilityModel

# Django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Django timezone
from django.utils import timezone

# Models
from companies.models import Company


class BuyerManager(VisibilityManager):
    """
    A custom buyer manager to deal with the denormalization
    of some compny fields in the creation of a buyer.
    """

    def create(self, company, **buyer_data):

        if buyer_data.get('display_name') is None:
            buyer_data['display_name'] = company.name

        if buyer_data.get('description') is None:
            buyer_data['description'] = company.description

        return super().create(
            company = company,
            **buyer_data
        )


class BuyerProfile(VisibilityModel):
    """
    Buyer profile of a company registered in the platform.
    It could be activated when the company deems necessary.
    """

    id = models.BigAutoField(primary_key = True)

    company = models.OneToOneField(Company, on_delete=models.PROTECT,
        help_text=_("Company owner of the buyer profile.")
    )

    display_name = models.CharField(
        help_text = _("""
            Name that is going to be displayed in the profile. This isn't 
            the real name of the company, is a completely election of the profile owner.\n
            By default the real company name is going to be selected."""), 
        max_length=60
    )

    description = models.CharField(
        help_text = _("""
            Description of the supplier that is going to be displayed 
            in the profile. Is indepent from the company desciption. \n
            But by default this value is going to be loaded with the description of the company"""),
        max_length=155, blank=True, null=True
    )

    contact_area_code = models.CharField(
        help_text = _('area code of the contact channel of a buyer profile'),
        max_length=5, blank = True, null = True
    )

    contact_phone = models.CharField(
        help_text = _('phone number of the contact channel of a buyer profile'),
        max_length=15, blank = True, null = True
    )

    contact_email = models.EmailField(
        help_text = _('email of the contact channel of a buyer profile'),
        blank = True, null = True
    )

    activation_date = models.DateTimeField(
        help_text = _('date when the profile was activated'), default=timezone.now
    )

    objects = BuyerManager()

    class Meta:
        db_table = 'buyer_profile'