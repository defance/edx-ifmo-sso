from django.conf import settings
from django.conf.urls import include, url
from path import path

import edxmako
import json
import logging

import lms.urls as lms_urls
import cms.urls as cms_urls

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


def run():

    # Patch template search paths
    TEMPLATE_PATH = path(__file__).dirname() / 'templates'
    settings.TEMPLATE_DIRS.insert(0, TEMPLATE_PATH)
    edxmako.paths.add_lookup('main', TEMPLATE_PATH, prepend=True)

    # Patch django configuration
    patch_config()

    # Inject urls
    lms_urls.urlpatterns.insert(0,
        url(r'', include('ifmo_sso.urls')),
    )
    cms_urls.urlpatterns.insert(0,
        url(r'', include('ifmo_sso.urls_studio')),
    )

