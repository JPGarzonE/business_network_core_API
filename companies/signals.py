# Companies / signals.py

from django.dispatch import Signal

post_product_delete = Signal(providing_args=["sender", "instance"])