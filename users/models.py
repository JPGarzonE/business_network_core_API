# Models Users

# Django
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib import auth
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _

# Django mail
from django.core.mail import send_mail

# Django timezone
from django.utils import timezone

# Models
from multimedia.models import Document, Media

# Utils
from enum import Enum


# Enum for entitites visibility
class VisibilityState(Enum):
    PRIVATE = 'Private'
    OPEN = 'Open'
    PERSONALIZED = 'Personalized'
    DELETED = 'Deleted'


class Deal(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=45)
    title = models.CharField(max_length=60)
    objetivo = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=155, blank=True, null=True)
    relationship = models.ForeignKey('Relationship', models.PROTECT)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'deal'
        unique_together = (('id', 'relationship'),)

class UserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user for the platform, without username,
    first_name and last_name.
    """
    
    email = models.EmailField(unique=True)

    username = models.CharField(max_length = 50, null = False, unique = True)

    verification = models.ForeignKey('Verification', models.PROTECT)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    is_client = models.BooleanField(
        'client',
        default=True,
        help_text=(
            'Help easily distinguish users and perform queries. '
            'Clients are the main type of user.'
        )
    )

    is_verified = models.BooleanField(
        'verified',
        default=False,
        help_text='Set to true when the user have verified its email address.'
    )

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    
    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'auth_user'

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Relationship(models.Model):
    requester = models.ForeignKey('User', models.PROTECT, related_name = 'relation_requester')
    addressed = models.ForeignKey('User', models.PROTECT, related_name = 'relation_addressed')
    type = models.CharField(max_length=30)
    verification = models.ForeignKey('Verification', models.PROTECT)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'relationship'
        unique_together = (('requester','addressed'),)


class Verification(models.Model):
    id = models.BigAutoField(primary_key=True)
    verified = models.BooleanField(default = False)

    class States(Enum):
        NONE = 'None'
        INPROGRESS = 'InProgress'
        STOPPED = 'Stopped'
        LOCKED = 'Locked'
        SUCCESS = 'Success'

    state = models.CharField(
        max_length=15,
        choices = [(stateOption, stateOption.value) for stateOption in States],
        default = States.NONE,
        null=False,
        blank=False,
    )

    application_date = models.DateTimeField(help_text = _('date when was generated'), default=timezone.now)
    finish_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'verification'