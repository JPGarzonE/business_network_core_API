from django.db import models
from django.utils.translation import ugettext_lazy as _

# Models
from companies.models import Product
from multimedia.models import Image

# Create your models here.

class ShowcaseSection(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=60)

    class Meta:
        db_table = 'showcasesection'

class ShowcaseProduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    tariff_heading = models.CharField(max_length = 20, blank = True, null = True)
    description = models.CharField(max_length=155, blank=True, null=True)
    principal_image = models.ForeignKey(Image, models.PROTECT, null = True)
    showcase_section = models.ForeignKey(ShowcaseSection, models.PROTECT)
    product = models.ForeignKey(Product, models.PROTECT)
    company_name = models.CharField(max_length=60)
    company_username = models.CharField(max_length=50)

    class Meta:
        db_table = 'showcaseproduct'