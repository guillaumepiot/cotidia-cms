from django import template
from django.utils.translation import get_language

register = template.Library()

from cms.settings import CMS_DEFAULT_LANGUAGE
from cms.models import Page

#
# Return the page URL for a specific language
#
@register.filter
def get_page_url(page, lang=None):
    if lang is None:
        lang = get_language()
    return page.get_absolute_url(lang)

#
# Build a Tree Node of published pages
#
@register.assignment_tag(takes_context=True)
def get_published_pages(context):
	return Page._tree_manager.filter(
		published=True, published_from=None)

#
# Returns the home page object
#
@register.assignment_tag
def home_page():
    pages = Page.objects.filter(home=True)
    if pages.count() > 0:
        return pages[0]
    else:
        return False