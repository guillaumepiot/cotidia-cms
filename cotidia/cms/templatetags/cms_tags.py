from django import template
from django.utils.translation import get_language

register = template.Library()

from cotidia.cms.settings import CMS_DEFAULT_LANGUAGE
from cotidia.cms.models import Page

#
# Return the page URL for a specific language
#
@register.filter
def get_page_url(page, lang=None):
    if lang is None:
        lang = get_language()
    return page.get_absolute_url(lang)

#
# Return the admin URL for a specific language
#
@register.filter
def get_admin_url(page, lang=None):
    return page.get_admin_url()

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

#
# Returns a page from its unique identifier
#
class PageBySlugNode(template.Node):
    def __init__(self, slug, varname):
        if slug[0] in ('"', "'"):
            self.slug = slug[1:-1]
            self.is_template_var = False
        else:
            self.slug = template.Variable(slug)
            self.is_template_var = True
        self.varname = varname
    def render(self, context):
        if self.is_template_var:
            self.slug = self.slug.resolve(context)
        self.pages = Page.objects.filter(slug=self.slug)
        if self.pages.count() > 0:
            context[self.varname] = self.pages[0]
        else:
            context[self.varname] = False
        return ''

@register.tag
def get_page_by_unique_identifier(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, slug, conjonction, varname  = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag must be in the following format: {% get_page_by_slug 'page-slug' as pagevar %}" % token.contents.split()[0])

    return PageBySlugNode(slug, varname)
