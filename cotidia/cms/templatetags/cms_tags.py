from django import template
from django.utils.translation import get_language

from cotidia.cms.models import Page
from cotidia.cms.conf import settings

register = template.Library()


@register.filter
def get_page_url(page, lang=None):
    """Return the page URL for a specific language."""
    if lang is None:
        lang = get_language()
    return page.get_absolute_url(lang)


@register.filter
def get_admin_url(page, lang=None):
    """Return the admin URL for a specific language."""
    return page.get_admin_url()


@register.simple_tag(takes_context=True)
def get_published_pages(context):
    """Build a Tree Node of published pages."""
    return Page._tree_manager.filter(
        published=True, published_from=None)


@register.simple_tag
def home_page():
    """Return the home page object."""
    pages = Page.objects.filter(home=True)
    if pages.count() > 0:
        return pages[0]
    else:
        return False


class PageBySlugNode(template.Node):
    """Return a page from its unique identifier."""

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
        tag_name, slug, conjonction, varname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            (
                "{} tag must be in the following format: "
                "{% get_page_by_slug 'page-slug' as pagevar %}"
            ).format(token.contents.split()[0])
        )

    return PageBySlugNode(slug, varname)


@register.inclusion_tag('cms/partials/embed_google_map.html')
def embed_google_map(lat, lng, zoom, address):
    if settings.CMS_GOOGLE_API_KEY is None:
        raise Exception("Please set the Google Map API Key: `CMS_GOOGLE_API_KEY`.")
    return {
        'lat': lat,
        'lng': lng,
        'zoom': zoom,
        'address': address,
        'CMS_GOOGLE_API_KEY': settings.CMS_GOOGLE_API_KEY
    }


@register.inclusion_tag('cms/partials/js_google_map.html')
def js_google_map(lat, lng, zoom, marker_icon):
    if settings.CMS_GOOGLE_API_KEY is None:
        raise Exception("Please set the Google Map API Key: `CMS_GOOGLE_API_KEY`.")
    return {
        'lat': lat,
        'lng': lng,
        'zoom': zoom,
        'marker_icon': marker_icon,
        'CMS_GOOGLE_API_KEY': settings.CMS_GOOGLE_API_KEY
    }
