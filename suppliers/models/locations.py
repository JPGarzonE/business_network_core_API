# Models locations

# Business Network API
from business_network_API.models import VisibilityModel

# Django
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

# Models
from suppliers.models import SupplierProfile
from multimedia.models import Image


class SupplierLocation(VisibilityModel):
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

    class Meta:
        db_table = 'supplier_location'

    @transaction.atomic
    def delete(self):
        """
        Validate if it's the principal location of a supplier before 
        soft deleting to manage additional deleting operations.
        """

        supplier = self.supplier

        if self == supplier.principal_location:
            supplier.principal_location = None
            supplier.save()

        super().delete()


class SupplierSaleLocation(VisibilityModel):
    """Location where a supplier sales."""

    id = models.BigAutoField(primary_key=True)
    
    country = models.CharField(max_length=50)
    
    city = models.CharField(max_length=50, blank=True, null=True)
    
    region = models.CharField(max_length=45, blank=True, null=True)
    
    supplier = models.ForeignKey(SupplierProfile, models.PROTECT)

    class Meta:
        db_table = 'supplier_sale_location'