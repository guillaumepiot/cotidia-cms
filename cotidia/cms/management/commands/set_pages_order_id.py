from django.core.management.base import BaseCommand

from cotidia.cms.models import Page


class Command(BaseCommand):
    help = "Go through all pages and set order ids."

    def recurse_children(self, page):
        order = 0
        for child in page.get_children():
            child.order_id = order
            child.save()
            order += 1
            if not child.is_leaf_node():
                print(child.order_id, "Parent", child)
                self.recurse_children(child)
            else:
                print(child.order_id, "Leaf", child)

    def handle(self, *args, **options):
        order = 0
        for page in Page.objects.get_originals():
            if page.is_root_node():
                page.order_id = order
                page.save()
                if not page.is_leaf_node():
                    print(page.order_id, "Parent", page)
                    self.recurse_children(page)
                else:
                    print(page.order_id, "Solo", page)
                    order += 1

        Page.objects.rebuild()
