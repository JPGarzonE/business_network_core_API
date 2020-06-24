# Multimedia models

# Django
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

# Models
# from users.models import Verification

# Utils
from enum import Enum

# Create your models here.

class Document(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(
        max_length=60,
        help_text=_('Is the name as the document is saved in the storage system'),
    )
    relative_path = models.TextField(help_text = _("path inside the storage (s3 bucket) - Not take in account domain (Ej: https://...)"), 
        blank = True)
    absolute_path = models.TextField(help_text = _("the complete path where is in the internet"), blank = True)
    purpose = models.CharField(
        max_length=35,
        null=False,
        blank=False,
        help_text=_("Describes the need that the document meets")
    )

    class Types(Enum):
        PDF = ('PDF', 'application/pdf'),

    type = models.CharField(
        help_text=_("Format, Ej: pdf, png, etc..."),
        max_length=17,
        choices = [(typeOption, typeOption.value) for typeOption in Types],
        blank = True
    )

    valid = models.BooleanField(
        default = None,
        null = True,
        help_text = _("Store if the document is in the correct format")
    )
    verification = models.ForeignKey('users.Verification', models.PROTECT, null = True, blank = True, related_name = 'documents')
    uploaded = models.BooleanField(help_text = _("stores if the file could be uploaded"), default=False)
    created_date = models.DateTimeField(_('date when was created'), default=timezone.now)

    class Meta:
        db_table = 'document'


class Media(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(help_text = _("the name of the file as is located"), max_length=120, blank=True)
    relative_path = models.TextField(help_text = _("path inside the storage (s3 bucket) - Not take in account domain (Ej: https://...)"), 
        blank = True)
    absolute_path = models.TextField(help_text = _("the complete path where is in the internet"), blank = True)
    width = models.CharField(max_length=8)
    height = models.CharField(max_length=8)
    size = models.CharField(max_length=8)

    class Types(Enum):
        JPEG = ('JPEG', 'image/JPEG'),
        JPG = ('JPG', 'image/JPG'),
        PNG = ('PNG', 'image/PNG'),
        VIDEO = ('MP4', 'video/mp4'),
        PDF = ('PDF', 'application/pdf'),

    type = models.CharField(
        max_length=17,
        choices = [(typeOption, typeOption.value) for typeOption in Types],
        null=False,
        blank=False,    
    )

    created_date = models.DateTimeField(_('date when was created'), default=timezone.now)
    uploaded = models.BooleanField(help_text = _("stores if the file could be uploaded"), default=False)

    class Meta:
        db_table = 'media'
