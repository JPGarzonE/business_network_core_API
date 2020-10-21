# Models
from companies.models import Product
from market.models import ShowcaseProduct, ShowcaseSection

# Signals
from companies.signals import post_product_delete, post_product_create
from django.db.models.signals import post_save
from django.dispatch import receiver


def get_showcase_section(name):
    showcase_section = ShowcaseSection.objects.filter( name__iexact = name.strip() )

    if showcase_section.exists():
        return showcase_section.first()
    else:
        return ShowcaseSection.objects.create(name = name )


def create_showcase_product(instance):
    showcase_section = get_showcase_section(name = instance.category)
    principal_image = instance.images.first() if instance.images and instance.images.first() else None

    ShowcaseProduct.objects.create(
        name = instance.name,
        tariff_heading = instance.tariff_heading,
        description = instance.description,
        principal_image = principal_image,
        product = instance,
        showcase_section = showcase_section,
        company_name = instance.company.name,
        company_username = instance.company.user.username
    )


def update_showcase_product(instance, showcase_product):
    principal_image = instance.images.first() if instance.images and instance.images.first() else None

    if not showcase_product.company_name:
        showcase_product.company_name = instance.company.name
    if not showcase_product.company_username:
        showcase_product.company_username = instance.company.user.username

    showcase_product.name = instance.name
    showcase_product.tariff_heading = instance.tariff_heading
    showcase_product.description = instance.description
    showcase_product.principal_image = principal_image
    showcase_product.showcase_section = get_showcase_section(name = instance.category)
    showcase_product.save()


@receiver(post_save, sender=Product)
def sync_showcase_update_product(sender, instance, created, **kwargs):
    showcase_product = ShowcaseProduct.objects.filter( product = instance ).first()

    if not created:
        update_showcase_product(instance, showcase_product)


@receiver(post_product_create, sender=Product)
def sync_showcase_create_product(sender, instance, created, **kwargs):

    if created:
        create_showcase_product(instance)


@receiver(post_product_delete, sender=Product)
def sync_delete_showcase_product(sender, instance, **kwargs):
    showcase_products = ShowcaseProduct.objects.filter( product = instance )

    for product in showcase_products:
        product.delete()