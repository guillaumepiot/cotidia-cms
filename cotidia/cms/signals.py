from django.dispatch import receiver

from cotidia.admin.signals import ordering_complete

from cotidia.cms.models import Page


@receiver(ordering_complete, sender=Page)
def handle_ordering_complete(sender, **kwargs):
    sender.objects.rebuild()
