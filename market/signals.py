# Models
from suppliers.models import Product
from market.models import ShowcaseProduct, ShowcaseSection

# Signals
from suppliers.signals import post_product_delete, post_product_create, post_product_update
from django.dispatch import receiver


def get_showcase_section(name):
    showcase_section = ShowcaseSection.objects.filter( name__iexact = name.strip() )

    if showcase_section.exists():
        return showcase_section.first()
    else:
        return ShowcaseSection.objects.create(name = name )


def create_showcase_product(instance):
    showcase_section = get_showcase_section(name = instance.category)

    ShowcaseProduct.objects.create(
        name = instance.name,
        tariff_heading = instance.tariff_heading,
        description = instance.description,
        principal_image = instance.principal_image,
        product = instance,
        showcase_section = showcase_section,
        supplier_name = instance.supplier.display_name,
        supplier_accountname = instance.supplier.company.accountname
    )


def update_showcase_product(instance, showcase_product):
    if not showcase_product.supplier_name:
        showcase_product.supplier_name = instance.supplier.display_name
    if not showcase_product.supplier_accountname:
        showcase_product.supplier_accountname = instance.supplier.company.accountname

    showcase_product.name = instance.name
    showcase_product.tariff_heading = instance.tariff_heading
    showcase_product.description = instance.description
    showcase_product.principal_image = instance.principal_image
    showcase_product.showcase_section = get_showcase_section(name = instance.category)
    showcase_product.save()


@receiver(post_product_update, sender=Product)
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