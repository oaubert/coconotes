from django.conf import settings

def siteinfo(request):
    """Defines a siteinfo variable.

    It allows site-wide customizations.
    """
    return {
        'siteinfo': {
            'variant': getattr(settings, 'SITE_VARIANT', ''),
            'debug': getattr(settings, 'DEBUG', False)
        }
    }
