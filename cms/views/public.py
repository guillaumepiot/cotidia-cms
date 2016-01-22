import json

from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.conf import settings
from django.utils import translation

from cms.models import Page, PageTranslation
from cms.settings import CMS_PREFIX, DEFAULT_LANGUAGE_FALLBACK


# Function to retrieve page object depending on previwe mode and language

def get_page(
    request, 
    model_class=Page,
    translation_class=PageTranslation,
    slug=False,
    preview=False,
    filter_args={}):

    # Deconstruct the slug to get the last element corresponding to the page we are looking for
    if slug and slug != CMS_PREFIX:

        slugs = slug.split('/')

        if CMS_PREFIX:
            if len(slugs) > 0 and slugs[0] == CMS_PREFIX:
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
                page_slugs = page_slugs[len(page_slugs)-slug_length:len(page_slugs)]
                
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
                        page_slugs = page_slugs[len(page_slugs)-slug_length:len(page_slugs)]
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

    if len(published)> 0:
        published = published[0]
        if published.translated() or DEFAULT_LANGUAGE_FALLBACK:
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
            if request.user.is_authenticated() and not preview == False:
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

                if not page_url == request.path and slug and not CMS_PREFIX:
                    return HttpResponseRedirect(page_url)

            # Assign is_preview to the request object for cleanliness
            request.is_preview = is_preview

            return f(request, page, slug, *args, **kwargs)
        return wrapper
    return wrap


@page_processor(model_class=Page, translation_class=PageTranslation)
def page(request, page, slug, *args, **kwargs):

    context = {'page':page}

    # Process kwargs to be passed back to the page context
    for key, value in iter(kwargs.items()):
        context[key] = value

    # Get the root page and then all its descendants, including self
    if hasattr(page, 'empty') and page.empty:
        nodes = []
    elif page.published_from == None:
        nodes = page.get_root().get_descendants(include_self=True)
    else:
        nodes = page.published_from.get_root().get_descendants(include_self=True)

    context['nodes'] = nodes

    return render_to_response(page.template, context, context_instance=RequestContext(request))


# def search(request, directory=False):
#     from whoosh.index import open_dir
#     from whoosh.qparser import QueryParser
#     from whoosh.query import And, Or, Term
#     from django.utils.translation import get_language
#     from django.contrib.contenttypes.models import ContentType
#     template = 'cmsbase/search.html'
#     results_objects = []

#     query = False
#     root = False
#     if request.POST or request.GET:
#         form = SearchForm(data=request.POST or request.GET)
#         if form.is_valid():

#             language_code = get_language()
#             query = form.cleaned_data['query']
#             ix = open_dir(cms_settings.SEARCH_INDEX_PATH)

#             with ix.searcher() as s:
#                 parser = QueryParser("content", ix.schema)
#                 myquery = parser.parse(query)
                
#                 # Filter results for our current language only
#                 allow_q = And([Term("language", language_code) , ])

#                 results = s.search(myquery, filter=allow_q, limit=None)

#                 results_objects = []

#                 for r in results:

#                     ct = ContentType.objects.get(model=r['content_type'].lower())
#                     obj_class = ct.model_class()
#                     obj = obj_class.objects.get(id=r['id'])

#                     result = {'title':obj.translated().title, 'url':obj.get_absolute_url(), 'breadcrumbs':obj.get_breadcrumbs(), 'content': obj.translated().content, 'content_type':r['content_type']}
#                     results_objects.append(result)
#     else:
#         form = SearchForm()

#     return render_to_response(template, {'query':query, 'results':results_objects, 'form':form, }, context_instance=RequestContext(request))

