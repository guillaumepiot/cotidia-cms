from django.conf import settings


def cms_settings(request):

    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_URL": settings.SITE_URL,
        "LANGUAGES": settings.LANGUAGES,
        "DEBUG": settings.DEBUG,
        "CMS_GA_CODE": settings.CMS_GA_CODE,
        "CMS_BROWSERCONFIG_TILE_COLOR": settings.CMS_BROWSERCONFIG_TILE_COLOR,
    }
