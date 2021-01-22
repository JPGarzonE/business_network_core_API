# Models verifications

# Django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Django timezone
from django.utils import timezone

# Models
from multimedia.models import File

# Utils
from enum import Enum


class CompanyVerification(models.Model):
    """Verification process that check if a company exist and is legal"""

    id = models.BigAutoField(primary_key = True)

    verified = models.BooleanField(
        default = False,
        help_text = _('Set to true when the verification process has ended succesfully')
    )

    class States(Enum):
        NONE = 'None'
        INPROGRESS = 'InProgress'
        STOPPED = 'Stopped'
        LOCKED = 'Locked'
        SUCCESS = 'Success'

    state = models.CharField(
        max_length=15,
        choices = [(stateOption, stateOption.value) for stateOption in States],
        default = States.NONE.value,
        null=False,
        blank=False,
    )

    application_date = models.DateTimeField(
        help_text = _('date when was the verification process was started'), 
        default=timezone.now
    )

    finish_date = models.DateTimeField(
        help_text = _('date when was the verification process was closed'), 
        blank=True, null=True
    )

    files = models.ManyToManyField(File, verbose_name=_("files"), through = "CompanyVerificationFile")

    class Meta:
        db_table = 'company_verification'


class CompanyVerificationFile(models.Model):
    """File that is part of a verification process."""

    id = models.BigAutoField(primary_key = True)

    company_verification = models.ForeignKey(
        CompanyVerification, models.PROTECT,
        help_text = _('Verification process that has been opened for verify a company.')
    )

    file = models.ForeignKey(
        File, models.CASCADE,
        help_text = _('File that is part of the company verification process')
    )

    class Meta:
        db_table = 'company_verification_file'