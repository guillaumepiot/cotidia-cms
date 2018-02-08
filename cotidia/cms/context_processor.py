from django.conf import settings


def cms_settings(request):

    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_URL": settings.SITE_URL,
        "LANGUAGES": settings.LANGUAGES,
        "DEBUG": settings.DEBUG,
        "CMS_GA_CODE": settings.CMS_GA_CODE,
        "CMS_GOOGLE_API_KEY": settings.CMS_GOOGLE_API_KEY,
        "CMS_BROWSERCONFIG_TILE_COLOR": settings.CMS_BROWSERCONFIG_TILE_COLOR,
    }
