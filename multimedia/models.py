# Multimedia models

# Django
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

# Utils
from enum import Enum


class File(models.Model):
    """Model that represent a file stored in the platform."""

    id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        max_length=60,
        help_text=_('Is the name as the file is saved in the storage system'),
    )

    relative_path = models.TextField(
        help_text = _("path inside the storage - Not take in account domain (Ej: https://...)"),
        null = True, blank = True
    )

    absolute_path = models.TextField(
        help_text = _("the complete path where is in the internet"),
        blank = True
    )

    size = models.CharField(
        help_text = _("Size of the file in bytes"), 
        max_length=7
    )

    class Types(Enum):
        PDF = ('PDF', 'application/pdf'),

    type = models.CharField(
        help_text=_("Format, Ej: application/pdf, etc..."),
        max_length=17,
        choices = [(typeOption, typeOption.value) for typeOption in Types],
        blank = True
    )

    uploaded = models.BooleanField(
        help_text = _("stores if the file could be uploaded"), 
        default=False
    )

    created_date = models.DateTimeField(
        help_text = _('date when was created'), 
        default=timezone.now
    )

    class Meta:
        db_table = 'file'


class Image(models.Model):
    """Model that represent an image stored in the platform."""

    id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        help_text = _("the name of the image as is located"), 
        max_length=120, blank=True
    )

    relative_path = models.TextField(
        help_text = _("path inside the storage - Not take in account domain (Ej: https://...)"), 
        blank = True
    )
    
    absolute_path = models.TextField(
        help_text = _("the complete path where is in the internet"), 
        blank = True
    )
    
    width = models.CharField(max_length=8)
    
    height = models.CharField(max_length=8)
    
    size = models.CharField(
        help_text = _("Size of the image in bytes"), 
        max_length=7
    )

    class Types(Enum):
        JPEG = ('JPEG', 'image/JPEG'),
        JPG = ('JPG', 'image/JPG'),
        PNG = ('PNG', 'image/PNG'),

    type = models.CharField(
        max_length=17,
        choices = [(typeOption, typeOption.value) for typeOption in Types],
        null=False,
        blank=False,    
    )

    created_date = models.DateTimeField(
        help_text = _('date when was created'), 
        default=timezone.now
    )

    uploaded = models.BooleanField(
        help_text = _("stores if the file could be uploaded"), 
        default=False
    )

    class Meta:
        db_table = 'image'


class Video(models.Model):
    """Model that represents a video stored in the platform."""

    id = models.BigAutoField(primary_key=True)
    
    name = models.CharField(
        help_text = _("the name of the video as is located"), 
        max_length=120, 
        blank=True 
    )

    relative_path = models.TextField( 
        help_text = _("path inside the storage - Not take in account domain (Ej: https://...)"), 
        blank = True
    )
    
    absolute_path = models.TextField(
        help_text = _("the complete path where is in the internet"),
        blank = True
    )

    length = models.FloatField( 
        help_text = _("Duration of the video in seconds"), 
        max_length = 5
    )

    size = models.CharField(help_text = _("Size of the video in bytes"), max_length=9)

    class Types(Enum):
        MP4 = ('MP4', 'video/mp4'),
        WEBM = ('WEBM', 'video/webm'),
        OGG = ('OGG', 'video/ogg'),

    type = models.CharField(
        max_length=17,
        choices = [(typeOption, typeOption.value) for typeOption in Types],
        null=False,
        blank=False,    
    )

    created_date = models.DateTimeField(
        help_text = _('date when was created'), 
        default=timezone.now
    )

    uploaded = models.BooleanField(
        help_text = _("stores if the file could be uploaded"), 
        default=False
    )

    class Meta:
        db_table = 'video'