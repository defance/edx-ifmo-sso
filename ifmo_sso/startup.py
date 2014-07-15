from django.conf import settings
from django.conf.urls import include, url
from path import path

import edxmako
import json
import logging


log = logging.getLogger(__name__)


def patch_config():

    IFMO_TOKENS_FILE = "ifmo.auth.json"

    IFMO_TOKENS = {}
    try:
        with open(settings.CONFIG_ROOT / IFMO_TOKENS_FILE) as ifmo_conf_file:
            IFMO_TOKENS = json.load(ifmo_conf_file)

        settings.LMS_BASE_URL = IFMO_TOKENS.get('LMS_BASE_URL')
        settings.CMS_BASE_URL = IFMO_TOKENS.get('CMS_BASE_URL')
        settings.SSO_PATH     = IFMO_TOKENS.get('SSO_PATH')

        settings.SSO_SECRET     = IFMO_TOKENS.get('SSO_SECRET')
        settings.SSO_REDIRECT   = settings.LMS_BASE_URL + IFMO_TOKENS.get('SSO_REDIRECT')
        settings.SSO_LOGOUTBACK = settings.LMS_BASE_URL + IFMO_TOKENS.get('SSO_LOGOUTBACK')

        settings.SSO_SECRET_STUDIO     = IFMO_TOKENS.get('SSO_SECRET_STUDIO')
        settings.SSO_REDIRECT_STUDIO   = settings.CMS_BASE_URL + IFMO_TOKENS.get('SSO_REDIRECT_STUDIO')
        settings.SSO_LOGOUTBACK_STUDIO = settings.CMS_BASE_URL + IFMO_TOKENS.get('SSO_LOGOUTBACK_STUDIO')

    except Exception as e:
        log.warning('Failed to load config for ifmo_sso')
        log.warning(e)


def patch_templates():
    template_path = path(__file__).dirname() / 'templates'
    edxmako.paths.add_lookup('main', template_path, prepend=True)


def _patch_variant_url(app_name, urls_module):
    app_urls = __import__('%s.urls' % (app_name,), fromlist=['urlpatterns'])
    app_urls.urlpatterns.insert(0, url(r'', include(urls_module)))
    log.info('%s successfully urls patched with %s' % (app_name, urls_module))


def patch_urls():
    for (app, urls) in [('lms', 'ifmo_sso.urls'), ('cms', 'ifmo_sso.urls_studio')]:
        try:
            _patch_variant_url(app, urls)
        except Exception:
            pass


def run():

    patch_templates()
    patch_config()
    patch_urls()

