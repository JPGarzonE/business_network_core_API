from django.db import models
from django.utils.translation import ugettext_lazy as _

# Models
from suppliers.models import Product
from multimedia.models import Image

# Create your models here.

class ShowcaseSection(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=60)

    class Meta:
        db_table = 'showcasesection'

class ShowcaseProduct(models.Model):
    id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        help_text = _('name or title as is going to be displayed the product'),
        max_length=50
    )
    
    tariff_heading = models.CharField(
        help_text = _('Value that is used in foreign trade to identify uniquely a product.'),
        max_length = 20, blank = True, null = True
    )
    
    description = models.TextField(
        help_text = _('description for add the principal characteristics of the product.'),
        blank=True, null=True
    )
    
    minimum_price = models.DecimalField(
        help_text = _("""Lower limit of the price. If there is no 
            maximum_price there is only going to be one absolute price."""),
        max_digits=15, decimal_places=2, null = True, blank = True
    )
    
    maximum_price = models.DecimalField(
        help_text = _("""Upper limit of the price. If this value exists means that
            there is a range of prices in which the companies can negotiate."""),
        max_digits=15, decimal_places=2, null = True, blank = True
    )

    measurement_unit = models.CharField(
        help_text = _('Type of unit that is used to measure and offer the product.'),
        max_length = 30, blank = True, null = True
    )

    minimum_purchase = models.CharField(
        help_text = _('minimum amount for which the product owner is willing to sell the product.'),
        max_length=30, blank=True, null=True
    )

    principal_image = models.ForeignKey(
        Image, models.PROTECT, null = True,
        help_text = _("""Image that appears in the cover of the product. 
            Is the first visible image everywhere.""")
    )
    
    showcase_section = models.ForeignKey(ShowcaseSection, models.PROTECT)

    product = models.ForeignKey(Product, models.PROTECT)
    
    supplier_name = models.CharField(
        max_length=60,
        help_text = _("name of the supplier that is selling the product")
    )
    
    supplier_accountname = models.CharField(
        max_length=50,
        help_text = _("accountname of the supplier that is selling the product")
    )

    class Meta:
        db_table = 'showcaseproduct'