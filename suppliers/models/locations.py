# Models locations

# constants
from companies.constants import VisibilityState

# Django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Models
from suppliers.models import SupplierProfile
from multimedia.models import Image


class SupplierLocation(models.Model):
    """Location where a supplier operates."""

    id = models.BigAutoField(primary_key=True)
    
    country = models.CharField(max_length=50)
    
    city = models.CharField(max_length=50, blank=True, null=True)
    
    region = models.CharField(max_length=45, blank=True, null=True)
    
    address = models.CharField(max_length=45, blank=True, null=True)
    
    zip_code = models.CharField(max_length=45, blank=True, null=True)
    
    latitude = models.DecimalField(
        help_text = _("""Option field for display the location 
            in digital maps with precission."""),
        max_digits = 9, decimal_places = 6, null = True, blank = True
    )

    longitude = models.DecimalField(
        help_text = _("""Option field for display the location 
            in digital maps with precission."""),
        max_digits = 9, decimal_places = 6, null = True, blank = True
    )
    
    image = models.ForeignKey(Image, models.CASCADE, 
        help_text = _("""Image of the headquarters of the supplier 
            or other image that represents the location."""),
        blank=True, null=True
    )
    
    supplier = models.ForeignKey(SupplierProfile, models.PROTECT)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'supplier_location'


class SupplierSaleLocation(models.Model):
    """Location where a supplier sales."""

    id = models.BigAutoField(primary_key=True)
    
    country = models.CharField(max_length=50)
    
    city = models.CharField(max_length=50, blank=True, null=True)
    
    region = models.CharField(max_length=45, blank=True, null=True)
    
    supplier = models.ForeignKey(SupplierProfile, models.PROTECT)

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'supplier_sale_location'