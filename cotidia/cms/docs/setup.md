Setup
=====

The CMS package requires the following dependencies to be installed:

- Django==1.8.4
- Pillow==2.9.0
- django-form-utils==1.0.3
- django-mptt==0.7.4
- django-reversion==1.9.3
- djangorestframework==3.2.4
- djrill==1.4.0

It also requires the Account app to manage users and other utils functions.

## Migrate the CMS tables

    $ python manage.py migrate cms

If you make changes to the models, then you will need to run a database 
migrations:
    
    $ python manage.py makemigrations cms

## Add CMS to the settings

    INSTALLED_APPS = (
        ...

        'account',
        'cms',
        'mptt',
        'rest_framework.authtoken',
    )

## CMS menu

The CMS build its own administration menu which can be inserted into the main
administration menu:

    {% include "admin/cms/includes/menu.html" %}

## CMS urls

The URLs are split into two categories:

- admin URLs
- api URLs
- public URLs

The URLs can be independently assigned:

    urlpatterns = [
        url(r'^admin/cms/', include('cms.urls.admin', namespace='cms-admin')),
        url(r'^api/cms/', include('cms.urls.api', namespace='cms-api')),
        url(r'^pages/', include('cms.urls.public', namespace='cms-public')),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

## Templates


    CMS_PAGE_TEMPLATES = (
        ('cms/page.html', 'Default page'),
        ('cms/page-sidebar-left.html', 'Page with left sidebar'),
        )

## Multiple languages

The CMS supports multiple languages and are defined using the following
settings:
    
    CMS_LANGUAGES = (
        ('en', "English"),
        ('fr', "French"),
    )

The default language is always the first in the list.

## Default language fallback

In the case of a multilingual site, we have two cases when it comes to a 
missing language:

- Return a 404 page
- Load the default language page

Depending on which behaviour works best for your website, you can set the
`DEFAULT_LANGUAGE_FALLBACK` setting to `True` to fallback, or `False` to return
404.

    DEFAULT_LANGUAGE_FALLBACK = False

## Support for localised URLs

Django 1.8 and above supports locale URLs. First you will need to add the
`LocaleMiddleware` to the middleware settings:

    django.middleware.locale.LocaleMiddleware

## API settings

You will need to specify the Django Rest Framework settings, with authentication
methods, and parsers:

    REST_FRAMEWORK = {
        # Use Django's standard `django.contrib.auth` permissions,
        # or allow read-only access for unauthenticated users.
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAdminUser',
        ),
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ),
        'DEFAULT_PARSER_CLASSES': (
            'rest_framework.parsers.JSONParser',
            'rest_framework.parsers.FormParser',
            'rest_framework.parsers.MultiPartParser',
        )
    }