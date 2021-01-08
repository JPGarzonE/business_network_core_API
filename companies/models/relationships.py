# Models relationships

# Constants
from companies.constants import VisibilityState

# Django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Models
from companies.models import Company, UnregisteredCompany


class Relationship(models.Model):
    """
    Relation that is established between 
    two companies inside the platform.
    """

    id = models.BigAutoField(primary_key=True)

    requester = models.ForeignKey(Company, models.PROTECT, related_name = 'relationship_requester')

    addressed = models.ForeignKey(Company, models.PROTECT, related_name = 'relationship_addressed')

    type = models.CharField(
        max_length=30, blank = True, null = True,
        help_text = _('Type of relationship that has been built between the companies')
    )

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'relationship'
        unique_together = (('requester','addressed'),)


class RelationshipRequest(models.Model):
    """
    Before establishing a relationship is required that both 
    companies in the relationship approve it. This model represents 
    the request that a company send to other to establish that relationship.
    """

    id = models.BigAutoField(primary_key=True)

    requester = models.ForeignKey(Company, models.PROTECT, related_name = 'relationship_request_requester')

    addressed = models.ForeignKey(Company, models.PROTECT, related_name = 'relationship_request_addressed')
    
    message = models.TextField(
        _("Message"), blank = True, null = True,
        help_text = _('Message that the company requester include in the relationship request')
    )
    
    blocked = models.BooleanField(
        _('blocked'), default = False,
        help_text = _("Indicates if the relationship wasn't accepted by the addressed company")
    )
    
    created_date = models.DateTimeField(
        help_text = _('date when the request was sent by the requester company'), 
        auto_now_add=True
    )
    
    last_updated = models.DateTimeField(
        help_text = _('date when the request was last updated by some of the members.'), 
        auto_now=True
    )

    class Meta:
        db_table = "relationship_request"


class UnregisteredRelationship(models.Model):
    """
    Relation that is established between a company that is registered 
    in the platform and another company that has not been registered yet.
    """

    requester = models.ForeignKey(
        Company, models.PROTECT, 
        related_name = 'unregistered_relationship_requester',
        help_text = _(
            'Is the company that request the relationship.'
            'It exist in the platform and is registered')
    )

    unregistered = models.ForeignKey(
        UnregisteredCompany, models.PROTECT,
        related_name = 'relationship_unregistered',
        help_text = _(
            'Is the company that is not official registered in the platform.'
            'It was created by another user that could not find its partners registered'
            'but wants to show it in its relationships, or was created by a sysadmin')
    )

    type = models.CharField(
        max_length=30, blank = True, null = True,
        help_text = _('Type of relationship between a registered and a non registered company.')
    )

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'unregistered_relationship'
        unique_together = (('requester','unregistered'),)
