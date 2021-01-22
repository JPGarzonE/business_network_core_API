# Models members

# Django
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CompanyMember(models.Model):
    """
    User member of a company. This user has access to 
    the company account according the assigned permissions.
    """

    id = models.BigAutoField(primary_key=True)

    company = models.ForeignKey(
        'Company', verbose_name = _('company account'), on_delete = models.PROTECT,
        help_text = _('Company that is accesible for its members (user).')
    )

    user = models.ForeignKey(
        'users.User', verbose_name = _('company employee'), on_delete = models.PROTECT,
        help_text = _('User that has access to the company account')
    )

    number_of_logins_in_supplier_profile = models.PositiveIntegerField( default = 0 )

    number_of_logins_in_buyer_profile = models.PositiveIntegerField( default = 0 )

    company_accountname = models.CharField(
        max_length = 60, null = False, unique = True,
        help_text = _("Attribute accountname of the company model. Denormalized for fast access.")
    )
    
    company_name = models.CharField(
        max_length=60, null = False, unique = True,
        help_text = _("Attribute name of the company model. Denormalized for fast access.")
    )

    user_email = models.EmailField(
        null = False, unique=True,
        help_text = _("Attribute email of the user model. Denormalized for fast access.")
    )

    user_username = models.CharField(
        max_length = 60, null = False, unique = True,
        help_text = _("Attribute username of the user model. Denormalized for fast access."),
    )

    user_full_name = models.CharField(
        max_length=50,
        help_text = _("Attribute full_name of the user model. Denormalized for fast access.")
    )

    class Meta:
        db_table = 'company_member'
        unique_together = (('company', 'user'),)