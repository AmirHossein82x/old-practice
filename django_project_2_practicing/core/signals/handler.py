from django.dispatch import receiver
from store.signals import order_create

@receiver(order_create)
def order_signal_check(sender, **kwargs):
    print(kwargs)