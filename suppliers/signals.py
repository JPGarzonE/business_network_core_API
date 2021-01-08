# Companies / signals.py

from django.dispatch import Signal

post_product_delete = Signal(providing_args=["sender", "instance"])

post_product_create = Signal(providing_args=["sender", "instance", "created"])

post_product_update = Signal(providing_args=["sender", "instance", "created"])