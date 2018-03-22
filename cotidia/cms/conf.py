from django.conf import settings

from appconf import AppConf


class CMSConf(AppConf):

    # The default page templates
    PAGE_TEMPLATES = (
        ('cms/page.html', 'Default page'),
    )

    # List available languages
    LANGUAGES = (
        ('en', "English"),
        ('fr', "French"),
    )

    DEFAULT_LANGUAGE = LANGUAGES[0]

    # Auto prefix
    PREFIX = None

    # Display default language
    # If the page doesn't exists in the current language, fall back to default
    # language. Set to False to not render if no language version available.

    DEFAULT_LANGUAGE_FALLBACK = False

    BROWSERCONFIG_TILE_COLOR = "#00abd3"

    GA_CODE = "XXXXXX"
    GOOGLE_API_KEY = None

    ENABLE_META_DATA = True

    class Meta:
        prefix = 'cms'
