# Models dna

# Constants
from companies.constants import VisibilityState

# Django
from django.db import models

# Models
from suppliers.models import SupplierProfile
from multimedia.models import Image


class DNAElement(models.Model):
    """
    DNA element that store different things that 
    make special and represents a Supplier profile.
    """

    id = models.BigAutoField(primary_key=True)

    title = models.CharField(max_length=45)
    
    category = models.CharField(max_length=45)
    
    image = models.ForeignKey(Image, models.CASCADE, blank=True, null=True)
    
    supplier = models.ForeignKey(SupplierProfile, models.PROTECT)
    
    description = models.CharField(max_length=155, blank=True, null=True)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'dna_element'