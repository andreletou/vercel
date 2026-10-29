from django.conf import settings


def site(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_LOGO_URL": settings.SITE_LOGO_URL,
    }
