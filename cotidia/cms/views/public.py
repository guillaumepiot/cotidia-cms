from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render

from cotidia.cms.models import Page, PageTranslation
from cotidia.cms.conf import settings


# Function to retrieve page object depending on previwe mode and language

def get_page(
        request,
        model_class=Page,
        translation_class=PageTranslation,
        slug=False,
        preview=False,
        filter_args={}):

    # Deconstruct the slug to get the last element corresponding to the
    # page we are looking for
    if slug and slug != settings.CMS_PREFIX:

        slugs = slug.split('/')

        if settings.CMS_PREFIX:
            if len(slugs) > 0 and slugs[0] == settings.CMS_PREFIX:
                slugs = slugs[1:]

        if len(slugs) == 1:
            last_slug = slugs[len(slugs)-1]
        elif len(slugs) > 1:
            last_slug = slugs[len(slugs)-1]
            # Get parent page:
            translation = translation_class.objects.filter(slug=last_slug, parent__published_from=None)

        published = []

        if preview:
            translation = translation_class.objects.filter(slug=last_slug, parent__published_from=None, **filter_args)
        else:
            translation = translation_class.objects.filter(slug=last_slug, parent__published=True, **filter_args).exclude(parent__published_from=None)

        # fetch the page that correspond to the complete url - as they can be multiple page with same slug but in different branches
        if translation.count() > 0:
            for t in translation:

                # We must align lengths of slug parameters to avoid a URL prefix set against the app
                # Eg: you may set up the cms app to run under /cms/, but because the slug will not contain '/cms/',
                # we must count backwards the number of parameters of slug, and add the same number from get_absolute_url.
                # that way the app prefix should be striped from the comparison
                slug_length = len(slugs)

                page_url = t.parent.get_absolute_url().strip('/')
                page_slugs = page_url.split('/')
                # Count from the end
                page_slugs = page_slugs[len(page_slugs) - slug_length:len(page_slugs)]

                # Are the slugs matching?
                if page_slugs == slugs:
                    published.append(t.parent)
                    continue
                else:
                    # No match? Now we should also check if we are looking at the right page but not in the right language
                    # So now we lookup other languages for the same page and see if there's a match
                    for lang in t.parent.get_translations():
                        page_url = lang.parent.get_absolute_url(lang.language_code).strip('/')
                        page_slugs = page_url.split('/')
                        page_slugs = page_slugs[len(page_slugs) - slug_length:len(page_slugs)]
                        if page_slugs == slugs:
                            published.append(t.parent)
                            continue

    else:
        if preview:
            published = model_class.objects.filter(home=True, published_from=None)
        else:
            # If no sulg provided get the page checked as home
            published = model_class.objects.filter(published=True, home=True).exclude(published_from=None)
            # If no page is checked as home, return the first one in the list
            if not published:
                published = model_class.objects.filter(published=True).exclude(published_from=None)[:1]

    if len(published) > 0:
        published = published[0]
        if published.translated() or settings.DEFAULT_LANGUAGE_FALLBACK:
            return published

    return None


# Page decorator
# Cover the basic handling such as page object lookup, redirect, 404, preview mode, language switching url switching
def page_processor(model_class=Page, translation_class=PageTranslation):
    def wrap(f):
        def wrapper(request, slug=False, *args, **kwargs):

            # Check if the preview variable is in the path
            preview = request.GET.get('preview', False)

            # Set preview to False by default
            is_preview = False

            # Make sure the user has the right to see the preview
            if request.user.is_authenticated() and request.user.has_perm("cms.change_page") and preview is not False:
                is_preview = True

            # Is it home page or not?
            if slug:
                page = get_page(request=request, model_class=model_class, translation_class=translation_class, slug=slug, preview=is_preview)
            else:
                page = get_page(request=request, model_class=model_class, translation_class=translation_class, preview=is_preview)

            # Check if any page exists at all
            # Then Raise a 404 if no page can be found
            if not page:
                # Any pages at all?
                if not model_class.objects.filter(published=True):
                    # Show CMS setup congratulations
                    page = model_class()
                    page.empty = True
                    page.template = 'cms/setup-complete.html'
                else:
                    raise Http404('This page could not be retrieved by the CMS')

            else:

                # Hard redirect if specified in page attributes
                if page.redirect_to:
                    return HttpResponseRedirect(page.redirect_to.get_absolute_url())
                if page.redirect_to_url:
                    return HttpResponseRedirect(page.redirect_to_url)

                # When you switch language it will load the right translation but stay on the same slug
                # So we need to redirect to the right translated slug if not on it already
                page_url = page.get_absolute_url()

                if not page_url == request.path and slug and not settings.CMS_PREFIX:
                    return HttpResponseRedirect(page_url)

            # Assign is_preview to the request object for cleanliness
            request.is_preview = is_preview

            return f(request, page, slug, *args, **kwargs)
        return wrapper
    return wrap


@page_processor(model_class=Page, translation_class=PageTranslation)
def page(request, page, slug, *args, **kwargs):

    context = {'page': page}

    # Process kwargs to be passed back to the page context
    for key, value in iter(kwargs.items()):
        context[key] = value

    # Get the root page and then all its descendants, including self
    if hasattr(page, 'empty') and page.empty:
        nodes = []
    elif page.published_from is None:
        nodes = page.get_root().get_descendants(
            include_self=True)
    else:
        nodes = page.published_from.get_root().get_descendants(
            include_self=True)

    context['nodes'] = nodes

    return render(request, page.template, context)


# App icons for Windows Metro UI
def browserconfig(request):
    content = """<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
  <msapplication>
    <tile>
      <square70x70logo src="{site_url}{static_url}ico/smalltile.png"/>
      <square150x150logo src="{site_url}{static_url}ico/mediumtile.png"/>
      <square310x310logo src="{site_url}{static_url}ico/largetile.png"/>
      <wide310x150logo src="{site_url}{static_url}ico/widetile.png"/>
      <TileColor>{color}</TileColor>
    </tile>
  </msapplication>
</browserconfig>""".format(
        site_url=settings.SITE_URL,
        static_url=settings.STATIC_URL,
        color=settings.CMS_BROWSERCONFIG_TILE_COLOR
    )

    return HttpResponse(content, content_type="text/xml")
