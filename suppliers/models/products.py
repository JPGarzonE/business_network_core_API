# Models products

# Constants
from companies.constants import VisibilityState

# Django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Models
from suppliers.models import Certificate, SupplierProfile
from multimedia.models import Image


class Currency(models.Model):
    """Currency that determines the types 
    of amounts handled on the platform"""

    id = models.BigAutoField(primary_key=True)
    
    name = models.CharField(max_length=45)
    
    code = models.CharField(
        help_text = _('Code that represents the currency'),
        max_length=6
    )
    
    region = models.CharField(
        help_text = _('Region where the currency come from'),
        max_length=50
    )
    
    is_active = models.BooleanField(
        help_text = _('Determines if the currency can be used in the platform'),
        default = True
    )

    class Meta:
        db_table = 'currency'


class Product(models.Model):
    """
    Product that a supplier offers in the platform.
    It is published in its profile and in the market
    being visible for all the buyers registered.
    """

    id = models.BigAutoField(primary_key=True)
    
    supplier = models.ForeignKey(SupplierProfile, models.PROTECT)
    
    name = models.CharField(
        help_text = _('name or title as is going to be displayed the product'),
        max_length=50
    )
    
    category = models.CharField(
        help_text = _('main category for classify the product'),
        max_length=60
    )

    minimum_price = models.DecimalField(
        help_text = _("""Lower limit of the price. If there is no 
            maximum_price there is only going to be one absolute price."""),
        max_digits=15, decimal_places=2
    )
    
    maximum_price = models.DecimalField(
        help_text = _("""Upper limit of the price. If this value exists means that
            there is a range of prices in which the companies can negotiate."""),
        max_digits=15, decimal_places=2, null = True, blank = True
    )
    
    price_currency = models.ForeignKey(
        Currency, models.PROTECT,
        help_text = _('Currency in which is configured the product prices')
    )

    measurement_unit = models.CharField(
        help_text = _('Type of unit that is used to measure and offer the product.'),
        max_length = 30, blank = True, null = True
    )
    
    tariff_heading = models.CharField(
        help_text = _('Value that is used in foreign trade to identify uniquely a product.'),
        max_length = 20, blank = True, null = True
    )
    
    minimum_purchase = models.CharField(
        help_text = _('minimum amount for which the product owner is willing to sell the product.'),
        max_length=30, blank=True, null=True
    )
    
    description = models.TextField(
        help_text = _('description for add the principal characteristics of the product.'),
        blank=True, null=True
    )

    certificates = models.ManyToManyField(
        Certificate, through = "ProductCertificate",
        help_text = _('Certificates that the product has.')
    )
    
    principal_image = models.ForeignKey(
        Image, on_delete=models.PROTECT, 
        blank=True, null=True, 
        related_name = '%(class)s_principal_image',
        help_text = _("""Image that appears in the cover of the product. 
            Is the first visible image everywhere.""")
    )
    
    secondary_images = models.ManyToManyField(
        Image, through = "ProductImage", 
        related_name = '%(class)s_secondary_images',
        help_text = _('Secondary images that shows the details of the product.')
    )

    visibility = models.CharField(
        max_length=20,
        choices = [(visibilityOption, visibilityOption.value) for visibilityOption in VisibilityState],
        default = VisibilityState.OPEN.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = 'product'

    def delete(self):
        self.visibility = VisibilityState.DELETED.value
        self.save()

    def hard_delete(self):
        super(Product, self).delete()


class ProductCertificate(models.Model):
    """Certificate that has a product."""

    id = models.BigAutoField(primary_key=True)
    
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    
    certificate = models.ForeignKey(Certificate, on_delete=models.PROTECT)

    class Meta:
        db_table = 'product_certificate'
        unique_together = (('product', 'certificate'),)


class ProductImage(models.Model):
    """Image that has a product."""

    id = models.BigAutoField(primary_key=True)
    
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    
    image = models.ForeignKey(Image, models.PROTECT, unique = False)

    class Meta:
        db_table = 'product_image'
        unique_together = (('product', 'image'),)