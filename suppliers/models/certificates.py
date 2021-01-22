# Models certificates

# Business Network API
from business_network_API.models import VisibilityModel

# Django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Models
from suppliers.models import SupplierProfile
from multimedia.models import Image


class Certificate(models.Model):
    """
    Certificate that probe some good practica or quality 
    in the products and proccesses of an organization.
    """

    id = models.BigAutoField(primary_key=True)
    
    name = models.CharField(max_length=60)
    
    description = models.CharField(
        help_text = _('Text that describe which aspect certifies the certificate.'),
        max_length=155, blank=True, null=True
    )

    logo = models.ForeignKey(Image, models.CASCADE, 
        help_text = _('Logo that represents the authority that emits the certificate'),
        blank=True, null=True
    )

    class Meta:
        db_table = 'certificate'


class SupplierCertificate(VisibilityModel):
    """
    Certificate that has a supplier.
    """

    id = models.BigAutoField(primary_key=True)
    
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.PROTECT)
    
    certificate = models.ForeignKey(Certificate, on_delete=models.PROTECT)

    class Meta:
        db_table = 'supplier_certificate'
        unique_together = (('supplier', 'certificate'),)